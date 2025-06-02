import time
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from src.models.message_model import Message
from src.models.room_model import Room
from src.models.user_model import User

from fastapi import WebSocket, WebSocketDisconnect, status


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[UUID, dict[UUID, WebSocket]] = {}

    @asynccontextmanager
    async def connect(
        self,
        websocket: WebSocket,
        room_id: UUID,
        user_id: UUID,
        username: str,
        email: str = None,
        role: str = "user",
        db: AsyncSession = None,
    ):
        """Создание соединения вебсокет-сесиии."""
        try:
            if not await self.authenticate_user(user_id, email, db):
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            if room_id not in self.active_connections:
                self.active_connections[room_id] = {}
            self.active_connections[room_id][user_id] = websocket
            await self.broadcast(f"Пользователь {username} зашел в чат", room_id, user_id, db, is_system=True)
            await self.send_users_update(room_id, db)
            if db:
                try:
                    user = await db.get(User, user_id)
                    if not user:
                        user = User(id=user_id, name=username, email=email, role=role, room_id=room_id)
                        db.add(user)
                    else:
                        user.room_id = room_id
                        if email:
                            user.email = email
                        if username:
                            user.name = username
                        if role:
                            user.role = role

                    await db.commit()
                except Exception:
                    await db.rollback()
                    raise
            yield
        finally:
            await self._safe_disconnect(room_id, user_id, db, username)

    async def authenticate_user(self, user_id: UUID, email: str, db: AsyncSession) -> bool:
        """Проверка аутентификации пользователя."""
        if not db:
            return True
        try:
            user = await db.get(User, user_id)
            if user:
                return True

            if email:
                result = await db.execute(select(User).where(User.email == email))
                return result.scalar_one_or_none() is not None
            return False
        except Exception:
            return False

    async def _safe_disconnect(self, room_id: UUID, user_id: UUID, db: AsyncSession, username: str):
        """Закрытие вебсокет сессии."""
        try:
            if room_id in self.active_connections and user_id in self.active_connections[room_id]:
                del self.active_connections[room_id][user_id]
                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]
                await self.send_users_update(room_id, db)
                if db:
                    await self.broadcast(
                        f"Пользователь {username} вышел из чата", room_id, user_id, db, is_system=True
                    )
        except KeyError:
            pass

    async def broadcast(self, message: str, room_id: UUID, sender_id: UUID, db: AsyncSession, is_system: bool = False):
        """Обработка сообщений в чате."""
        try:
            async with db.begin_nested():
                room = await db.get(Room, room_id)
                user = await db.get(User, sender_id)
                if not room or not user:
                    return

                if not is_system:
                    db_message = Message(text=message, room_id=room_id, user_id=sender_id)
                    db.add(db_message)
                    await db.flush()
                    timestamp = db_message.created_at.timestamp()
                else:
                    timestamp = time.time()

                if room.message_history is None:
                    room.message_history = []

                room.message_history.append(
                    {
                        "text": message,
                        "username": user.name,
                        "timestamp": timestamp,
                        "role": user.role,
                        "type": "system" if is_system else "message",
                    }
                )
                flag_modified(room, "message_history")
                await db.commit()
                await self._send_messages(room_id, sender_id, message, user, is_system)

        except Exception as e:
            if db:
                await db.rollback()
            raise e

    async def _send_messages(self, room_id: UUID, sender_id: UUID, message: str, user: User, is_system: bool):
        message_payload = {
            "type": "system" if is_system else "message",
            "text": message,
            "username": user.name,
            "timestamp": time.time(),
            "role": user.role,
            "is_self": False,
        }
        if room_id not in self.active_connections:
            return
        for uid, websocket in self.active_connections[room_id].items():
            try:
                payload = message_payload.copy()
                payload["is_self"] = uid == sender_id
                await websocket.send_json(payload)
            except WebSocketDisconnect:
                await self._safe_disconnect(room_id, uid, None)

    async def send_users_update(self, room_id: UUID, db: AsyncSession):
        if room_id not in self.active_connections:
            return
        result = await db.execute(select(User).where(User.room_id == room_id))
        users = result.scalars().all()
        user_list = [{"username": user.name, "email": user.email, "role": user.role} for user in users]
        payload = {"type": "users_update", "users": user_list}
        for websocket in self.active_connections[room_id].values():
            try:
                await websocket.send_json(payload)
            except WebSocketDisconnect:
                pass


manager = ConnectionManager()
