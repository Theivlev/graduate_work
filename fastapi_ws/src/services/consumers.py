import json

from aio_pika.abc import AbstractChannel, AbstractIncomingMessage
from src.db.postgres import get_async_session
from src.schemas.rabbit_schema import WsMessage
from src.schemas.recomendation_schema import GeneralRecommendationResponseDTO
from src.services.ws_service import ChatService
from src.utils.movies import get_movie_by_id


async def on_ws_message(message: AbstractIncomingMessage, channel: AbstractChannel):
    """Получение сообщения авторизации по письму из брокера."""

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


async def on_recom_message(message: AbstractIncomingMessage, channel: AbstractChannel):
    """Получение сообщения рекомендации из брокера."""

    async with message.process(ignore_processed=True):
        try:
            data = GeneralRecommendationResponseDTO.model_validate(json.loads(message.body.decode()))
            if data.recommendations:
                movies = []
                for recom in data.recommendations:
                    movie = await get_movie_by_id(recom.movie_id)
                    if movie:
                        movies.append(movie.title)
                film_list = ", ".join(movies)

                async for session in get_async_session():
                    chat_service = await ChatService.create(session)
                    await chat_service.add_mailing_message(
                        message=f"Рекомендуем посмотреть следующие фильмы: {film_list}.",
                    )
            await message.ack()
        except Exception:
            await message.reject(requeue=False)
