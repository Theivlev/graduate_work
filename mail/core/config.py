import logging

from pydantic_settings import BaseSettings, SettingsConfigDict


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


class SMTPSettings(BaseSettings):
    """Настройки SMTP."""

    host: str
    port: int
    user: str
    password: str
    use_tls: bool

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="SMTP_")


class MailQueueSettings(BaseSettings):
    """Настройки имён exchange, очередей и routing key для email-рассылки."""

    mail_exchange: str
    retry_exchange: str
    failed_exchange: str

    mail_queue: str
    retry_queue: str
    failed_queue: str
    recom_queue: str

    mail_routing_key: str
    retry_routing_key: str
    failed_routing_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="MAIL_")


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


rabbit_settings = RabbitMQSettings()  # type: ignore
grpc_settings = GRPCSettings()  # type: ignore
smtp_settings = SMTPSettings()  # type: ignore
mail_queue_settings = MailQueueSettings()  # type: ignore
postgres_settings = PostgresSettings()  # type: ignore

# Настройки логирования
LOGGER_FORMAT = "%(asctime)s [%(levelname)s] - %(message)s"
LOGGER_SETTINGS = {
    "level": logging.INFO,
    "format": LOGGER_FORMAT,
    "handlers": [
        logging.StreamHandler(),
    ],
}
logging.basicConfig(**LOGGER_SETTINGS)  # type: ignore

TEMPLATES_DIR = "/app/templates"
