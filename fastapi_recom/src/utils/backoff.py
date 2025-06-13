import asyncio
import logging
from functools import wraps
from http import HTTPStatus

from fastapi import HTTPException

logger = logging.getLogger(__name__)


class ServiceError(HTTPException):
    pass


class UnavailableServiceError(ServiceError):
    def __init__(self, detail: str = 'service is unavailable, retry later', **kwargs):
        super().__init__(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=detail, **kwargs)


class NotFoundServiceError(ServiceError):
    def __init__(self, detail: str = 'not found', **kwargs):
        super().__init__(status_code=HTTPStatus.NOT_FOUND, detail=detail, **kwargs)


def backoff(
    expected_exceptions: tuple[type[Exception], ...],
    attempts: int = 4,
    start_sleep_time: float = 0.05,
    factor: int = 2,
    border_sleep_time: int = 10,
):
    """
        Функция для повторного выполнения асинхронной функции.
        В случае возникновения ошибки.
        Использует экспоненциальный рост времени ожидания.
        """
    def func_wrapper(func: callable):
        @wraps(func)
        async def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            for _ in range(attempts):
                try:
                    return await func(*args, **kwargs)
                except expected_exceptions:
                    sleep_time = min(sleep_time * 2**factor, border_sleep_time)
                    await asyncio.sleep(sleep_time)

            raise UnavailableServiceError()

        return inner

    return func_wrapper
