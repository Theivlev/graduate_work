import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from src.db.postgres import engine
from src.models.film import Movies
from src.models.user import Users
from src.rabbitmq.broker import broker
from src.rabbitmq.enums import RoutingKeys
from src.rabbitmq.exchanges import EXCHANGES
from src.rabbitmq.queues import QUEUES
from src.schemas.actions_user import ActionsUserDTO
from src.services.actions import actions_service
from src.services.similarity import similarity_service
from src.services.vector import vector_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


db_session = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, class_=AsyncSession)


@broker.subscriber(QUEUES[RoutingKeys.ACTIONS], EXCHANGES[RoutingKeys.ACTIONS])
async def actions_user(
    message: ActionsUserDTO,
):
    """Обрабатывает сообщения о действиях пользователя из RabbitMQ."""
    try:
        async with db_session() as session:
            await actions_service.save_action(action_dto=message, session=session)
        async with db_session() as session:
            await vector_service.compute_user_vector(user_id=message.user_id, session=session)
        async with db_session() as session:
            await vector_service.compute_movie_vector(movie_id=message.movie_id, session=session)
        async with db_session() as session:
            users = (await session.execute(select(Users))).scalars().all()
            for other_user in users:
                if other_user.id != message.user_id:
                    await similarity_service.compute_user_similarity(
                        user1_id=message.user_id, user2_id=other_user.id, session=session
                    )
        async with db_session() as session:
            movies = (await session.execute(select(Movies))).scalars().all()
            for other_movie in movies:
                if other_movie.id != message.movie_id:
                    await similarity_service.compute_movie_similarity(
                        movie1_id=message.movie_id, movie2_id=other_movie.id, session=session
                    )

            await session.commit()
    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")
