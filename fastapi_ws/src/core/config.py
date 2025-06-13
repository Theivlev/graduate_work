from logging import config as logging_config

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .logger import LOGGING_CONFIG

logging_config.dictConfig(LOGGING_CONFIG)


class ProjectSettings(BaseSettings):
    """Настройки FastAPI."""

    static_path: str = "src/static"
    templates_path: str = "src/templates"
    name: str
    summary: str
    version: str
    terms_of_service: str
    tags: list = Field(
        default=[
            {
                "name": "chat",
                "description": "Operations with chat.",
            },
        ]
    )
    debug: bool = False
    superuser_name: str
    superuser_api_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="PROJECT_WS_")


class RedisSettings(BaseSettings):
    """Настройки Redis."""

    host: str
    port: int
    user: str
    password: str
    db_index: int
    dsn: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="REDIS_")

    def model_post_init(self, __context):
        """Формируем DSN после загрузки переменных."""
        self.dsn = f"redis://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_index}"


class PostgresSettings(BaseSettings):
    """Настройки Postgres."""

    db: str
    host: str
    port: int
    user: str
    password: str
    dsn: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="POSTGRES_")

    def model_post_init(self, __context):
        """Формируем DSN после загрузки переменных."""
        self.dsn = f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class RabbitMQSettings(BaseSettings):
    """Настройки RabbitMQ."""

    host: str
    user: str
    password: str
    port: int

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="RABBITMQ_")


class GRPCSettings(BaseSettings):
    """Настройки для подключения к gRPC серверу."""

    auth_grpc_host: str
    auth_grpc_port: int

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class MailQueueSettings(BaseSettings):
    """Настройки имён exchange, очередей и routing key для email-рассылки."""

    mail_exchange: str
    retry_exchange: str
    failed_exchange: str

    mail_queue: str
    retry_queue: str
    failed_queue: str

    mail_routing_key: str
    retry_routing_key: str
    failed_routing_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="MAIL_")


class WsQueueSettings(BaseSettings):
    """Настройки имён exchange, очередей и routing key для websocket сервиса."""

    ws_queue: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="WS_")


project_settings = ProjectSettings()  # type: ignore
redis_settings = RedisSettings()  # type: ignore
postgres_settings = PostgresSettings()  # type: ignore
mail_queue_settings = MailQueueSettings()  # type: ignore
rabbit_settings = RabbitMQSettings()  # type: ignore
grpc_settings = GRPCSettings()  # type: ignore
ws_settings = WsQueueSettings()  # type: ignore
