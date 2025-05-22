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
        """Формируем DSN после загрузки переменных"""
        self.dsn = f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


project_settings = ProjectSettings()  # type: ignore
redis_settings = RedisSettings()  # type: ignore
postgres_settings = PostgresSettings()  # type: ignore
