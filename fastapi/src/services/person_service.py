from dataclasses import dataclass
from functools import lru_cache
from http import HTTPStatus
from typing import List

from opentelemetry import trace
from opentelemetry.trace import SpanKind
from src.db.abstract_db import AbstractDAO
from src.db.elastic_dao import ElasticDAO, get_elastic
from src.models.person import PersonInfoDTO

from fastapi import Depends, HTTPException

tracer = trace.get_tracer(__name__)


@lru_cache()
def get_person_service(
    db: ElasticDAO = Depends(get_elastic),
) -> "PersonService":
    return PersonService(db)


@dataclass
class PersonService:
    """Сервис для работы с персонами."""

    db: AbstractDAO
    index: str = "persons"

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
                return PersonInfoDTO(**doc)
            except Exception as e:
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                raise

    async def search(
        self, page_size: int = 50, page_number: int = 1, full_name: str | None = None
    ) -> List[PersonInfoDTO]:
        """
        Выполняет поиск персон по имени.
        """

        with tracer.start_as_current_span(
            "service.search",
            kind=SpanKind.CLIENT,
            attributes={
                "page_size": page_size,
                "page_number": page_number,
                "full_name": full_name,
                "index": self.index,
            },
        ) as span:
            try:
                filters = {}

                if full_name:
                    filters["full_name"] = full_name

                response = await self.db.search(
                    table=self.index,
                    offset=(page_number - 1) * page_size,
                    limit=page_size,
                    filters=filters,
                )

                if not response:
                    span.set_attribute("error", True)
                    span.set_attribute("error.message", "persons not found")
                    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="persons not found")

                span.set_attribute("persons_count", len(response))
                return [PersonInfoDTO(**hit) for hit in response]
            except Exception as e:
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                raise
