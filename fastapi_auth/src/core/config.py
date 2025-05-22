from logging import config as logging_config
from typing import Optional

from pydantic import EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .logger import LOGGING_CONFIG

logging_config.dictConfig(LOGGING_CONFIG)


class ProjectSettings(BaseSettings):
    # FastAPI
    project_auth_name: str
    project_auth_summary: str
    project_auth_version: str
    project_auth_terms_of_service: str
    project_auth_tags: list = Field(
        default=[
            {
                "name": "auth",
                "description": "Operations with auth.",
            },
            {
                "name": "users",
                "description": "Operations with users.",
            },
            {
                "name": "roles",
                "description": "Operations with roles.",
            },
        ]
    )

    # Auth
    secret: str = "SECRET"
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None
    jwt_lifetime_seconds: int = 3600
    jwt_refresh_lifetime_seconds: int = 86400
    min_password_length: int = 3

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


class AuthSettings(BaseSettings):
    """Настройки авторизации."""

    secret: str = "SECRET"
    first_superuser_email: EmailStr | None = None
    first_superuser_password: str | None = None
    jwt_lifetime_seconds: int = 3600
    min_password_lenght: int = 3

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class YandexSettings(BaseSettings):
    """Настройки Yandex."""

    client_id: str
    client_secret: str
    redirect_uri_login: str
    redirect_uri_logout: str
    auth_url_login: str
    auth_url_logout: str
    token_url: str
    user_info_url: str
    revoke_token_url: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="YANDEX_")

    def model_post_init(self, __context):
        """Формируем DSN после загрузки переменных"""

        self.auth_url_login = f"https://oauth.yandex.ru/authorize?response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri_login}"
        self.auth_url_logout = f"https://oauth.yandex.ru/authorize?response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri_logout}"


class VkSettings(BaseSettings):
    """Настройки VK."""

    client_id: str
    client_secret: str
    code_challenge_method: str
    redirect_uri_login: str
    redirect_uri_logout: str
    auth_url: str
    token_url: str
    user_info_url: str
    logout_url: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="VK_")


class JaegerSettings(BaseSettings):
    """Настройки Jaeger."""

    host_name: str
    port: int
    service_name_auth: str
    dsn: str
    endpoint: str
    debug: bool

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="JAEGER_")

    def model_post_init(self, __context):
        """Формируем DSN после загрузки переменных."""

        self.dsn = f"http://{self.host_name}:{self.port}/{self.endpoint}"


class RabbitMQSettings(BaseSettings):
    """Настройки RabbitMQ."""

    host: str
    user: str
    password: str
    port: int

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="RABBITMQ_")


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


class MailQueueSettings(BaseSettings):
    """Настройки имён exchange, очередей и routing key для email-рассылки."""

    mail_exchange: str = "mail_exchange"
    retry_exchange: str = "retry_exchange"
    failed_exchange: str = "failed_exchange"

    mail_queue: str = "mail_queue"
    retry_queue: str = "mail_retry_queue"
    failed_queue: str = "failed_queue"

    mail_routing_key: str = "mail"
    failed_routing_key: str = "failed"

    redirect_url: str
    url_confirm: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="MAIL_")


project_settings = ProjectSettings()  # type: ignore
redis_settings = RedisSettings()  # type: ignore
postgres_settings = PostgresSettings()  # type: ignore
auth_settings = AuthSettings()  # type: ignore
yandex_settings = YandexSettings()  # type: ignore
vk_settings = VkSettings()  # type: ignore
jaeger_settings = JaegerSettings()  # type: ignore
rabbit_settings = RabbitMQSettings()  # type: ignore
sentry_settings = SentrySettings()  # type: ignore
mail_queue_settings = MailQueueSettings()  # type: ignore
