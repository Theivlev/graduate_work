from dataclasses import dataclass
from functools import lru_cache
from http import HTTPStatus
from typing import Any, Dict, List, Optional

from opentelemetry import trace
from opentelemetry.trace import SpanKind
from src.db.abstract_db import AbstractDAO
from src.db.elastic_dao import ElasticDAO, get_elastic
from src.models.genre import GenreDTO

from fastapi import Depends, HTTPException

tracer = trace.get_tracer(__name__)


@lru_cache()
def get_genre_service(
    db: ElasticDAO = Depends(get_elastic),
) -> "GenreService":
    return GenreService(db)


@dataclass
class GenreService:
    """Сервис для работы с жанрами."""

    db: AbstractDAO
    index: str = "genres"

    async def get_by_id(self, entity_id: str):
        """
        Получает жанр по ID.
        """

        with tracer.start_as_current_span(
            "service.get_by_id",
            kind=SpanKind.CLIENT,
            attributes={
                "entity_id": entity_id,
                "index": self.index,
            },
        ) as span:
            try:
                doc = await self.db.get(table=self.index, id_obj=entity_id)

                if not doc:
                    span.set_attribute("error", True)
                    span.set_attribute("error.message", f"{self.index} not found")
                    raise HTTPException(
                        status_code=HTTPStatus.NOT_FOUND,
                        detail=f"{self.index} not found",
                    )

                span.set_attribute("found", True)
                return GenreDTO(**doc)
            except Exception as e:
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                raise

    async def search(
        self,
        page_number: int = 1,
        page_size: int = 50,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[GenreDTO]:
        """
        Возвращает список жанров из Elasticsearch с учётом пагинации и (опционально) фильтрации.
        """
        if filters is None:
            filters = {}

        # Для поиска с пагинацией используем offset/limit
        offset = (page_number - 1) * page_size

        with tracer.start_as_current_span(
            "service.search",
            kind=SpanKind.CLIENT,
            attributes={
                "page_number": page_number,
                "page_size": page_size,
                "filters": filters,
                "index": self.index,
            },
        ) as span:
            try:
                response = await self.db.search(
                    table=self.index,
                    limit=page_size,
                    offset=offset,
                    filters=filters,
                )

                if not response:
                    span.set_attribute("error", True)
                    span.set_attribute("error.message", "genres not found")
                    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genres not found")

                span.set_attribute("genres_count", len(response))
                return [GenreDTO(**hit) for hit in response]
            except Exception as e:
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                raise
