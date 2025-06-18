import abc

from pydantic import AnyUrl


class BaseConfig(abc.ABC):
    """Базовый класс для клиента."""

    def __init__(self, dsn: AnyUrl, connect: any = None):
        self.dsn = dsn
        self.connect = connect

    @abc.abstractmethod
    def reconnect(self) -> any:
        """Переподключить соединение"""

    def close(self) -> None:
        """Закрыть соединение клиента."""
        if self.connection:
            self.connection.close()

    @property
    def connection(self) -> any:
        """Получить/восстановить соединение."""
        return self.connect if self.connect else self.reconnect()
