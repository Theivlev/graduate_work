from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rabbitmq.broker import broker
from rabbitmq.enums import RoutingKeys
from rabbitmq.exchanges import EXCHANGES
from rabbitmq.queues import QUEUES

from src.db.postgres import get_async_session
from src.schemas.actions_user import ActionsUserDTO
from src.services.actions import ActionsService, get_actions
from src.services.similarity import SimilarityService, get_similarity_service
from src.services.vector import VectorService, get_vector_service
from src.models.film import Movies
from src.models.user import User



@broker.subscriber(QUEUES[RoutingKeys.ACTIONS], EXCHANGES[RoutingKeys.ACTIONS])
async def actions_user(
    message: ActionsUserDTO,
    session: AsyncSession = Depends(get_async_session),
    actions_service: ActionsService = Depends(get_actions),
    vector_service: VectorService = Depends(get_vector_service),
    similarity_service: SimilarityService = Depends(get_similarity_service),
):
    """Обрабатывает сообщения о действиях пользователя из RabbitMQ."""
    try:

        await actions_service.save_action(message)

        user_id = UUID(message.user_id) if isinstance(message.user_id, str) else message.user_id
        movie_id = UUID(message.movies_id) if isinstance(message.movies_id, str) else message.movies_id
        await vector_service.compute_user_vector(user_id)
        await vector_service.compute_movie_vector(movie_id)

        users = (await session.execute(select(User))).scalars().all()
        for other_user in users:
            if other_user.id != user_id:
                await similarity_service.compute_user_similarity(user_id, other_user.id)

        movies = (await session.execute(select(Movies))).scalars().all()
        for other_movie in movies:
            if other_movie.id != movie_id:
                await similarity_service.compute_movie_similarity(movie_id, other_movie.id)

        await session.commit()
    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")
