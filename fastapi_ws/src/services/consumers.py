from aio_pika.abc import AbstractChannel, AbstractIncomingMessage
from src.db.postgres import get_async_session
from src.schemas.rabbit_schema import WsMessage
from src.services.ws_service import ChatService


async def on_ws_message(message: AbstractIncomingMessage, channel: AbstractChannel):
    """Получение сообщения из брокера."""

    async with message.process(ignore_processed=True):
        try:
            data = WsMessage.model_validate_json(message.body.decode())
            if data.event_type == "user_verified":
                async for session in get_async_session():
                    chat_service = await ChatService.create(session)
                    await chat_service.create_personal_room(
                        email=data.email,
                        fullname=data.fullname,
                        message=f"Добро пожаловать,{data.fullname} в наш чат!",
                    )
            await message.ack()
        except Exception:
            await message.reject(requeue=False)
