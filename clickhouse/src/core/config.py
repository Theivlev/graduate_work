from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки"""

    kafka_brokers: list[str]
    clickhouse_nodes: list[str]

    bootstrap_servers: str
    group_id: str
    topic: str
    partitions: int
    replicas: int
    replication_factor: int
    time_to_retain_data: str
    load_batch_size: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()  # type: ignore
