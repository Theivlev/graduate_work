import logging
from uuid import UUID

from fastapi import Depends
from faststream import FastStream
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.rabbitmq.broker import broker
from src.rabbitmq.enums import RoutingKeys
from src.rabbitmq.exchanges import EXCHANGES
from src.rabbitmq.queues import QUEUES

from src.db.postgres import get_async_session
from src.sсhemas.actions_user import ActionsUserDTO
from src.models.film import Movies
from src.models.user import Users
from src.services.actions import actions_service
from src.services.similarity import similarity_service
from src.services.vector import vector_service
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.db.postgres import engine


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


db_session = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)


@broker.subscriber(QUEUES[RoutingKeys.ACTIONS], EXCHANGES[RoutingKeys.ACTIONS])
async def actions_user(
    message: ActionsUserDTO,
):
    """Обрабатывает сообщения о действиях пользователя из RabbitMQ."""
    try:
        async with db_session() as session:

            user_id = UUID(message.user_id) if isinstance(message.user_id, str) else message.user_id
            movie_id = UUID(message.movies_id) if isinstance(message.movies_id, str) else message.movies_id
            logger.info(f'ЗАХОДИММММММ')
            await actions_service.save_action(action_dto=message, session=session)
            return
            await vector_service.compute_user_vector(user_id, session=session)
            await vector_service.compute_movie_vector(movie_id)

            users = (await session.execute(select(Users))).scalars().all()
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
