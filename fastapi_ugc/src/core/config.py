from logging import config as logging_config

from pydantic import Field, MongoDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from .logger import LOGGING_CONFIG

logging_config.dictConfig(LOGGING_CONFIG)


class ProjectSettings(BaseSettings):
    """Настраивает класс для чтения переменных окружения.."""

    name: str
    summary: str
    version: str
    terms_of_service: str
    tags: list = Field(
        default=[
            {
                "name": "bookmarks",
                "description": "Operations with bookmarks.",
            },
            {
                "name": "likes",
                "description": "Operations with likes.",
            },
            {
                "name": "reviews",
                "description": "Operations with reviews.",
            },
        ]
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="PROJECT_SOCIAL_")


class MongoSettings(BaseSettings):
    """Настраивает класс для чтения переменных окружения MognoDB."""

    ugc_dsn: MongoDsn
    ugc_db: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="MONGO_")


class AuthGrpcSettings(BaseSettings):
    """Настраивает класс для чтения переменных окружения gRPC."""

    host: str
    port: int

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="AUTH_GRPC_")


class KafkaSettings(BaseSettings):
    """Настраивает класс для чтения переменных окружения Kafka."""

    host: str
    topic: str = "movies"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="KAFKA_")


class RabbitMQSettings(BaseSettings):
    """Настройки RabbitMQ."""

    host: str
    user: str
    password: str
    port: int

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="RABBITMQ_")


project_settings = ProjectSettings()  # type: ignore
mongo_settings = MongoSettings()  # type: ignore
auth_grpc_settings = AuthGrpcSettings()  # type: ignore
kafka_settings = KafkaSettings()  # type: ignore
rabbit_mq_settings = RabbitMQSettings()  # type: ignore
