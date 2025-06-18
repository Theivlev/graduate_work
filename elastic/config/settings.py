from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки DSN."""

    elasticsearch_dsn: AnyHttpUrl
    postgres_dsn: PostgresDsn
    redis_dsn: RedisDsn
    batch_size: int
    timeout: float

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
