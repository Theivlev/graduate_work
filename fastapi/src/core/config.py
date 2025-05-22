from logging import config as logging_config

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .logger import LOGGING_CONFIG

logging_config.dictConfig(LOGGING_CONFIG)


class ProjectSettings(BaseSettings):
    # FastAPI
    project_name: str
    project_summary: str
    project_version: str
    project_terms_of_service: str
    project_tags: list = Field(
        default=[
            {
                "name": "films",
                "description": "Operations with films.",
            },
            {
                "name": "genres",
                "description": "Operations with genres.",
            },
            {
                "name": "persons",
                "description": "Operations with persons.",
            },
        ]
    )

    auth_grpc_host: str
    auth_grpc_port: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    debug: bool = False


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


class ElasticSettings(BaseSettings):
    """Настройки Elasticsearch."""

    host: str
    port: int
    dsn: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="ELASTICSEARCH_")

    def model_post_init(self, __context):
        """Формируем DSN после загрузки переменных."""

        self.dsn = f"http://{self.host}:{self.port}/"


class JaegerSettings(BaseSettings):
    """Настройки Jaeger."""

    host_name: str
    port: int
    service_name_films: str
    dsn: str
    endpoint: str
    debug: bool

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="JAEGER_")

    def model_post_init(self, __context):
        """Формируем DSN после загрузки переменных."""

        self.dsn = f"http://{self.host_name}:{self.port}/{self.endpoint}"


class SentrySettings(BaseSettings):
    """Настройки Sentry."""

    host: str
    port: int
    key: str
    dsn: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="SDK_SENTRY_")

    def model_post_init(self, __context):
        """Формируем DSN после загрузки переменных."""

        self.dsn = f"http://{self.key}@{self.host}:{self.port}/1"


project_settings = ProjectSettings()  # type: ignore
redis_settings = RedisSettings()  # type: ignore
elastic_settings = ElasticSettings()  # type: ignore
jaeger_settings = JaegerSettings()  # type: ignore
sentry_settings = SentrySettings()  # type: ignore
