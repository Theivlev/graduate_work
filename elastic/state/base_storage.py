import abc


class BaseStorage(abc.ABC):
    """Базовый класс для хранилища."""

    @abc.abstractmethod
    def save_state(self, key: str, value: str) -> None:
        """Сохранить состояние в хранилище."""

    @abc.abstractmethod
    def retrieve_state(self, key: str) -> str | None:
        """Извлечь состояние из хранилища."""
