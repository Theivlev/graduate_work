from dataclasses import dataclass
from functools import lru_cache
from http import HTTPStatus
from typing import List

from opentelemetry import trace
from opentelemetry.trace import SpanKind
from src.db.abstract_db import AbstractDAO
from src.db.elastic_dao import ElasticDAO, get_elastic
from src.models.film import MovieBaseDTO, MovieInfoDTO

from fastapi import Depends, HTTPException

tracer = trace.get_tracer(__name__)


@lru_cache()
def get_film_service(
    db: ElasticDAO = Depends(get_elastic),
) -> "FilmService":
    return FilmService(db)


@dataclass
class FilmService:
    """Сервис для работы с фильмами."""

    db: AbstractDAO
    index: str = "movies"

    async def get_by_id(self, entity_id: str):
        """
        Получает объект по ID.
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
                return MovieInfoDTO(**doc)
            except Exception as e:
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                raise

    async def search(
        self,
        genre: str | None = None,
        page_size: int = 50,
        page_number: int = 1,
        sort: str = "imdb_rating",
        title: str | None = None,
    ) -> List[MovieBaseDTO]:
        """
        Получает список фильмов.
        с поддержкой фильтрации, сортировки и пагинации.
        """

        with tracer.start_as_current_span(
            "service.search",
            kind=SpanKind.CLIENT,
            attributes={
                "genre": genre,
                "page_size": page_size,
                "page_number": page_number,
                "sort": sort,
                "title": title,
                "index": self.index,
            },
        ) as span:
            try:
                filters = {}

                if genre:
                    filters["genre.name"] = genre
                if title:
                    filters["title"] = title

                response = await self.db.search(
                    table=self.index,
                    offset=(page_number - 1) * page_size,
                    limit=page_size,
                    sort=[{sort: "desc"}],
                    filters=filters,
                )

                if not response:
                    span.set_attribute("error", True)
                    span.set_attribute("error.message", "films not found")
                    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")

                span.set_attribute("films_count", len(response))
                return [MovieBaseDTO(**hit) for hit in response]
            except Exception as e:
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                raise
