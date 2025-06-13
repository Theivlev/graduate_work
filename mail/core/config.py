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

    mail_exchange: str = "mail_exchange"
    retry_exchange: str = "retry_exchange"
    failed_exchange: str = "failed_exchange"

    mail_queue: str = "mail_queue"
    retry_queue: str = "mail_retry_queue"
    failed_queue: str = "failed_queue"

    mail_routing_key: str = "mail"
    retry_routing_key: str = "retry"
    failed_routing_key: str = "failed"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="MAIL_")


rabbit_settings = RabbitMQSettings()  # type: ignore
grpc_settings = GRPCSettings()  # type: ignore
smtp_settings = SMTPSettings()  # type: ignore
mail_queue_settings = MailQueueSettings()  # type: ignore

# Настройки логирования
LOGGER_FORMAT = "%(asctime)s [%(levelname)s] - %(message)s"
LOGGER_SETTINGS = {
    "level": logging.INFO,
    "format": LOGGER_FORMAT,
    "handlers": [
        logging.StreamHandler(),
    ],
}
logging.basicConfig(**LOGGER_SETTINGS)

TEMPLATES_DIR = "/app/templates"
