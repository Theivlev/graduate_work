from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from src.models.message_model import Message
from src.models.room_model import Room
from src.models.user_model import User

from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[UUID, dict[UUID, WebSocket]] = {}

    @asynccontextmanager
    async def connect(
        self, websocket: WebSocket, room_id: UUID, user_id: UUID, username: str, role: str, db: AsyncSession
    ):
        await websocket.accept()
        try:
            if room_id not in self.active_connections:
                self.active_connections[room_id] = {}
            self.active_connections[room_id][user_id] = websocket
            async with db.begin():
                user = await db.get(User, user_id)
                if not user:
                    user = User(id=user_id, name=username, role=role, room_id=room_id)
                    db.add(user)
                    await db.commit()
            yield
        finally:
            await self._safe_disconnect(room_id, user_id, db)

    async def _safe_disconnect(self, room_id: UUID, user_id: UUID, db: AsyncSession):
        try:
            if room_id in self.active_connections and user_id in self.active_connections[room_id]:
                del self.active_connections[room_id][user_id]
                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]
                await self.broadcast(f"Пользователь {user_id} вышел из чата", room_id, user_id, db, is_system=True)
        except KeyError:
            pass

    async def broadcast(self, message: str, room_id: UUID, sender_id: UUID, db: AsyncSession):
        try:
            async with db.begin():
                room = await db.get(Room, room_id)
                user = await db.get(User, sender_id)
                if not room or not user:
                    return
                db_message = Message(text=message, room_id=room_id, user_id=sender_id)
                db.add(db_message)
                await db.flush()
                if room.message_history is None:
                    room.message_history = []
                room.message_history.append(
                    {
                        "text": message,
                        "username": user.name,
                        "timestamp": db_message.created_at.timestamp(),
                        "role": user.role,
                        "type": "message",
                    }
                )
                flag_modified(room, "message_history")
                await db.commit()

                # Отправляем сообщение участникам
                await self._send_messages(room_id, sender_id, db_message, user)

        except Exception as e:
            print(f"Ошибка: {str(e)}")
            await db.rollback()
            raise e

    async def _send_messages(self, room_id: UUID, sender_id: UUID, message: Message, user: User):
        message_payload = {
            "type": "message",
            "text": message.text,
            "username": user.name,
            "timestamp": message.created_at.timestamp(),
            "role": user.role,
            "is_self": False,
        }

        for user_id, websocket in self.active_connections[room_id].items():
            try:
                payload = message_payload.copy()
                payload["is_self"] = user_id == sender_id
                await websocket.send_json(payload)
            except WebSocketDisconnect:
                await self._safe_disconnect(room_id, user_id)


manager = ConnectionManager()
