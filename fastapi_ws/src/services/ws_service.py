import json
from uuid import UUID, uuid4

from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.db.connections import manager
from src.db.postgres import get_async_session
from src.models.room_model import Room
from src.models.user_model import User

from fastapi import Depends, WebSocket


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @classmethod
    async def create(cls, db: AsyncSession = Depends(get_async_session)):
        return cls(db)

    async def handle_websocket_connection(self, websocket: WebSocket, room_id: UUID, user_id: UUID):
        username = websocket.query_params.get("username")
        role = websocket.query_params.get("role", "user")

        async with manager.connect(websocket, room_id, user_id, username, role, self.db):
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

    async def _handle_history_request(self, websocket: WebSocket, room_id: UUID):
        async with self.db.begin():
            stmt = select(Room).where(Room.id == room_id)
            result = await self.db.execute(stmt)
            room = result.scalar_one_or_none()

            if room:
                await self.db.refresh(room)
                await websocket.send_text(
                    json.dumps({"type": "history", "messages": room.message_history or []}, ensure_ascii=False)
                )

    async def join_chat(self, username: str, room_id: UUID, role: str):
        if not username:
            return JSONResponse({"success": False, "error": "Требуется имя пользователя"}, status_code=400)

        if role not in ["user", "admin"]:
            role = "user"

        user_id = uuid4()
        redirect_url = f"/ws/v1/chat/{room_id}/{user_id}?username={username}&role={role}"
        return JSONResponse(
            {"success": True, "room_id": str(room_id), "user_id": str(user_id), "redirect_url": redirect_url}
        )

    async def create_room(self, username: str, name: str):
        if not username or not name:
            return JSONResponse(
                {"success": False, "error": "Требуется указать имя пользователя и название комнаты"}, status_code=400
            )

        room_id = uuid4()
        user_id = uuid4()

        async with self.db.begin():
            room = Room(id=room_id, name=name)
            self.db.add(room)
            user = User(id=user_id, name=username, role="admin", room_id=room_id)
            self.db.add(user)
            await self.db.commit()

        redirect_url = f"/ws/v1/chat/{room_id}/{user_id}?username={username}&role=admin"
        return JSONResponse(
            {"success": True, "room_id": str(room_id), "user_id": str(user_id), "redirect_url": redirect_url}
        )

    async def get_rooms(self):
        try:
            stmt = select(Room).options(selectinload(Room.users))
            result = await self.db.execute(stmt)
            rooms = result.scalars().all()

            rooms_list = []
            for room in rooms:
                rooms_list.append({"id": str(room.id), "name": room.name, "users_count": len(room.users)})

            return {"success": True, "rooms": rooms_list}
        except Exception as e:
            return JSONResponse({"success": False, "error": f"Internal server error {e}"}, status_code=500)

    async def switch_room(self, user_id: UUID, old_room_id: UUID, new_room_id: UUID, username: str, role: str):
        if role != "admin":
            return JSONResponse(
                {"success": False, "error": "Только администратор может менять комнаты"}, status_code=403
            )

        async with self.db.begin():
            stmt = select(Room).where(Room.id == new_room_id)
            result = await self.db.execute(stmt)
            if not result.scalar_one_or_none():
                return JSONResponse({"success": False, "error": "Комната не найдена"}, status_code=404)

            stmt = select(User).where(User.id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                user.room_id = new_room_id
                await self.db.commit()

        redirect_url = f"/ws/v1/chat/{new_room_id}/{user_id}?username={username}&role={role}"
        return JSONResponse({"success": True, "redirect_url": redirect_url})


async def get_chat_service(db: AsyncSession = Depends(get_async_session)) -> ChatService:
    return await ChatService.create(db)
