import json
import time
from uuid import UUID

from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified
from src.db.connections import manager
from src.db.postgres import get_async_session
from src.models.room_model import Room
from src.models.user_model import User
from src.services.grpc.grpc_client_mail import GRPCAuthClient

from fastapi import Depends, WebSocket, status


class ChatService:
    """Сервис работы с вебсокетом."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.grpc_client = GRPCAuthClient()

    @classmethod
    async def create(cls, db: AsyncSession = Depends(get_async_session)):
        """Обработка для базы данных."""
        return cls(db)

    async def handle_websocket_connection(
        self, websocket: WebSocket, room_id: UUID, user_id: UUID, username: str, email: str = None, role: str = "user"
    ):
        """Создание соединения с Вебсокетом."""

        async with manager.connect(websocket, room_id, user_id, username=username, email=email, role=role, db=self.db):
            try:
                while True:
                    data = await websocket.receive_text()
                    try:
                        message_data = json.loads(data)
                        if message_data.get("command") == "get_history":
                            await self._handle_history_request(websocket, room_id)
                            continue
                        await manager.broadcast(message_data.get("text", data), room_id, user_id, self.db)
                    except json.JSONDecodeError:
                        await manager.broadcast(data, room_id, user_id, self.db)
            except Exception:
                await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

    async def _handle_history_request(self, websocket: WebSocket, room_id: UUID):
        """Получение истории сообщений для чата."""
        async with self.db.begin():
            stmt = select(Room).where(Room.id == room_id)
            result = await self.db.execute(stmt)
            room = result.scalar_one_or_none()
            if room:
                await self.db.refresh(room)
                await websocket.send_text(
                    json.dumps({"type": "history", "messages": room.message_history or []}, ensure_ascii=False)
                )

    async def get_user_by_email(self, email: str) -> User:
        """Получение пользователя по почте."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_or_create_personal_room(self, email: str) -> Room:
        """Получение или создание комнаты для пользователя."""
        user = await self.get_user_by_email(email)
        if user and user.room_id:
            return await self.db.get(Room, user.room_id)
        room = Room(name=f"Комната пользователя {email}")
        self.db.add(room)
        await self.db.flush()
        if not user:
            user = User(name=email.split("@")[0], email=email, role="user", room_id=room.id)
            self.db.add(user)
        else:
            user.room_id = room.id
        await self.db.commit()
        return room

    async def create_room(self, name: str) -> Room:
        """Создание новой комнаты."""
        room = Room(name=name)
        self.db.add(room)
        await self.db.commit()
        await self.db.refresh(room)
        return room

    async def get_all_rooms(self):
        """Получение всех комнат с пользователями."""
        stmt = select(Room).options(selectinload(Room.users))
        result = await self.db.execute(stmt)
        rooms = result.scalars().all()
        return [{"id": str(room.id), "name": room.name, "users_count": len(room.users)} for room in rooms]

    async def switch_room(self, user_id: UUID, new_room_id: UUID, username: str, email: str, role: str):
        """Переключение между комнатами."""
        user = await self.db.get(User, user_id)
        if not user:
            return {"success": False, "error": "Пользователь не найден"}
        room = await self.db.get(Room, new_room_id)
        if not room:
            return {"success": False, "error": "Комната не найдена"}
        user.room_id = new_room_id
        await self.db.commit()
        redirect_url = f"/ws/v1/chat/{new_room_id}/{user_id}?username={username}&email={email}&role={role}"
        return {"success": True, "redirect_url": redirect_url}

    async def get_user_rooms(self, user_id: UUID):
        """Получение комнат пользователя."""
        user = await self.db.get(User, user_id)
        if not user or not user.room_id:
            return []
        room = await self.db.get(Room, user.room_id)
        return [{"id": str(room.id), "name": room.name}] if room else []

    async def add_user_to_room(self, room_id: UUID, email: str):
        """Добавление пользователя в комнату администратором."""
        print(email, room_id)
        room = await self.db.get(Room, room_id)
        if not room:
            return {"success": False, "error": "Комната не найдена"}
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return {"success": False, "error": "User not found"}
        if user.room_id == room_id:
            return {"success": False, "error": f"Пользователь уже в комнате {user.room_id}"}
        user.room_id = room.id
        print(user.room_id, room_id)
        await self.db.commit()
        await self.db.refresh(user)
        return {"success": True}

    async def remove_user_from_room(self, room_id: UUID, email: str):
        """Удаление пользователя из комнаты администратором."""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return {"success": False, "error": "Пользователь не найден"}
        if user.room_id != room_id:
            return {"success": False, "error": "Пользователь не в этой комнате"}
        default_room = await self._get_or_create_default_room()
        user.room_id = default_room.id
        await self.db.commit()
        await self.db.refresh(user)
        return {"success": True}

    async def delete_room(self, room_id: UUID):
        """Удаление комнаты пользователем."""
        room = await self.db.get(Room, room_id)
        if not room:
            return {"success": False, "error": "Комната не найдена"}
        default_room = await self._get_or_create_default_room()
        stmt = select(User).where(User.room_id == room_id)
        result = await self.db.execute(stmt)
        users = result.scalars().all()
        for user in users:
            user.room_id = default_room.id
        await self.db.delete(room)
        await self.db.commit()
        return {"success": True}

    async def _get_or_create_default_room(self) -> Room:
        """Получение или создание временной комнаты."""
        stmt = select(Room).where(Room.name == "Default Room")
        result = await self.db.execute(stmt)
        room = result.scalar_one_or_none()
        if not room:
            room = Room(name="Default Room")
            self.db.add(room)
            await self.db.commit()
        return room

    async def get_all_users(self):
        """Получение всех пользователей."""
        stmt = select(User)
        result = await self.db.execute(stmt)
        users = result.scalars().all()
        return [{"id": str(user.id), "name": user.name, "email": user.email, "role": user.role} for user in users]

    async def create_personal_room(self, email: str, fullname: str, message: str):
        """Создает персональную комнату для пользователя при подтверждении email"""
        room_name = f"Комната пользователя {fullname}"
        if not fullname or not room_name:
            return JSONResponse(
                {"success": False, "error": "Требуется указать имя пользователя и название комнаты"}, status_code=400
            )
        try:
            async with self.db.begin():
                room = Room(name=room_name)
                if room.message_history is None:
                    room.message_history = []
                room.message_history.append(
                    {
                        "text": message,
                        "username": fullname,
                        "timestamp": time.time(),
                        "role": "user",
                        "type": "message",
                    }
                )
                flag_modified(room, "message_history")
                self.db.add(room)
                await self.db.flush()
                user = User(name=fullname, role="user", room_id=room.id, email=email)
                self.db.add(user)
                await self.db.commit()
            redirect_url = f"/ws/v1/chat/{room.id}/{user.id}?username={user.name}&email={user.email}&role={user.role}"
            return {"success": True, "room_id": str(room.id), "user_id": str(user.id), "redirect_url": redirect_url}
        except Exception as e:
            await self.db.rollback()
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    async def _add_mailing_message(self, message: str):
        """Рассылка рекомендательных сообщений во все комнаты."""
        try:
            result = await self.db.execute(select(Room))
            rooms = result.scalars().all()
            for room in rooms:
                if room.message_history is None:
                    room.message_history = []
                room.message_history.append(
                    {
                        "text": message,
                        "username": "Бот рекомендаций",
                        "timestamp": time.time(),
                        "role": "user",
                        "type": "message",
                    }
                )
                flag_modified(room, "message_history")

            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise e


async def get_chat_service(db: AsyncSession = Depends(get_async_session)) -> ChatService:
    return await ChatService.create(db)
