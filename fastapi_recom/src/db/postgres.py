import asyncio
import logging
import os
import re
import uuid

from alembic import command
from alembic.config import Config
from redis import asyncio as aioredis
from sqlalchemy import UUID, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Mapped, declarative_base, declared_attr, mapped_column, sessionmaker
from src.core.config import postgres_settings, project_settings

instance_id = os.getenv("HOSTNAME", "unknown_instance")
logging.basicConfig(
    level=logging.INFO,
    format=f"%(asctime)s [%(name)s.{instance_id}] %(levelname)s - %(message)s",
)
logger = logging.getLogger("src.db.postgres")

metadata = MetaData()


class PreBase:
    @declared_attr
    def __tablename__(self) -> str:
        """Добавляет название таблицы по названию класса в метаданные модели в стиле snake_case."""
        return re.sub(r"(?<!^)(?=[A-Z])", "_", self.__name__).lower()

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, sort_order=-1)


Base = declarative_base(cls=PreBase, metadata=metadata)
engine = create_async_engine(postgres_settings.dsn, echo=project_settings.debug)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def create_database():
    logger.info("Инициализация базы данных")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы успешно созданы")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        raise


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
