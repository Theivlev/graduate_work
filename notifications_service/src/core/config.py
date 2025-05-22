from logging import config as logging_config

from pydantic import Field, MongoDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from .logger import LOGGING_CONFIG

logging_config.dictConfig(LOGGING_CONFIG)


class Settings(BaseSettings):
    """Настраивает класс для чтения переменных окружения.."""

    project_auth_name: str
    project_auth_summary: str
    project_auth_version: str
    project_auth_terms_of_service: str

    mongo_notify_dsn: MongoDsn = Field(..., env='MONGO_NOTIFY_DSN')
    mongo_notify_db: str = Field(..., env='MONGO_NOTIFY_DB')

    auth_grpc_host: str
    auth_grpc_port: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class RabbitMQSettings(BaseSettings):
    """Настройки RabbitMQ."""

    host: str
    user: str
    password: str
    port: int

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="RABBITMQ_")


project_settings = Settings()
rabbit_settings = RabbitMQSettings()
