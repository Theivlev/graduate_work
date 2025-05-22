from enum import IntEnum
from typing import Tuple

from fastapi import Query


class PaginationLimits(IntEnum):
    MIN_PAGE = 0
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100

    @staticmethod
    def get_pagination_params(
        page_number: int = Query(default=MIN_PAGE, ge=MIN_PAGE, description="Номер страницы"),
        page_size: int = Query(
            default=DEFAULT_PAGE_SIZE, ge=MIN_PAGE + 1, le=MAX_PAGE_SIZE, description="Размер страницы"
        ),
    ) -> Tuple[int, int]:
        return page_number, page_size
