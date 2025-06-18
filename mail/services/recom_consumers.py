import json
import logging

from aio_pika.abc import AbstractChannel, AbstractIncomingMessage
from schemas.recomendation import UserRecommendationResponseDTO
from services.smtp import send_email_smtp
from utils.movies import get_movie_by_id

from .grpc.grpc_client_mail import get_auth_client

logger = logging.getLogger(__name__)


async def on_recom_message(message: AbstractIncomingMessage, channel: AbstractChannel):
    async with message.process(ignore_processed=True):
        try:
            data = UserRecommendationResponseDTO.model_validate(json.loads(message.body.decode()))
            grpc_client = get_auth_client()

            user = await grpc_client.get_user_info(user_id=data.user_id)
            movies = []
            for recom in data.recommendations:
                movie = await get_movie_by_id(recom.movie_id)
                if movie:
                    movies.append(movie.title)
            film_list = "\n- ".join(movies)
            await send_email_smtp(
                email=user.email,
                subject="Ваши рекомендации к просмотру",
                template="recomendation.html",
                data={
                    "full_name": f"{user.name} {user.surname}",
                    "subject": "Ваши рекомендации к просмотру",
                    "film_list": film_list,
                },
            )
            logger.info("Письмо успешно отправлено.")
        except Exception:
            await message.reject(requeue=False)
