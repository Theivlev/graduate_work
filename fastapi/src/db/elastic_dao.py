import logging

from elasticsearch import AsyncElasticsearch, NotFoundError, TransportError
from elasticsearch.exceptions import ConnectionError as ElasticsearchError
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from src.db.abstract_db import AbstractDAO
from src.utils.backoff import backoff

from fastapi import Request

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class ElasticDAO(AbstractDAO):
    """Класс для работы с Elasticsearch."""

    def __init__(self, elastic: AsyncElasticsearch):
        """Конструктор класса."""
        self.elastic = elastic

    @backoff(ElasticsearchError)
    async def get(self, table: str, id_obj: str) -> dict[str, str] | None:
        """Получение объекта по id."""
        with tracer.start_as_current_span(
            "elasticsearch.get",
            kind=SpanKind.CLIENT,
            attributes={
                "el.table": table,
                "el.id_obj": id_obj,
            },
        ) as span:
            try:
                doc = await self.elastic.get(index=table, id=id_obj)
                return doc.get("_source")
            except NotFoundError as e:
                span.set_attribute("error", True)
                span.set_attribute("error.message", f"Объект не найден: {e}")
                logger.warning(f"Объект в {table} не найден: id={id_obj}")
            except TransportError as e:
                span.set_attribute("error", True)
                span.set_attribute("error.message", f"Ошибка транспортировки: {e}")
                logger.error(f"При запросе id={id_obj} к {table} произошла ошибка: {e}")
            return None

    @backoff(ElasticsearchError)
    async def search(
        self,
        table: str,
        offset: int = 0,
        limit: int = 50,
        sort: list[dict[str, str]] | None = None,
        filters: dict[str, any] | None = None,
    ):
        """Поиск объектов в таблице."""
        with tracer.start_as_current_span(
            "elasticsearch.search",
            kind=SpanKind.CLIENT,
            attributes={
                "el.operation": "search",
                "el.table": table,
                "el.offset": offset,
                "el.limit": limit,
            },
        ) as span:
            span.set_attribute("el.operation", "search")
            span.set_attribute("el.table", table)
            span.set_attribute("el.offset", offset)
            span.set_attribute("el.limit", limit)
            must_conditions = []

            filter_conditions = []

            if filters is None:
                filters = {}

            search_query = {
                "size": limit,
                "from": offset,
                "query": {"bool": {"must": []}},
            }

            for key, value in filters.items():
                if key.count(".") == 1:
                    path = key.split(".")[0]
                    filter_conditions.append(
                        {"nested": {"path": path, "query": {"bool": {"must": [{"match": {key: value}}]}}}}
                    )
                if key.count(".") == 0:
                    must_conditions.append({"multi_match": {"query": value, "fields": [key]}})

            if must_conditions:
                search_query["query"]["bool"]["must"] = must_conditions

            if filter_conditions:
                search_query["query"]["bool"]["filter"] = filter_conditions

            if sort:
                search_query["sort"] = sort

            span.set_attribute("el.search_query", str(search_query))
            try:
                response = await self.elastic.search(index=table, body=search_query)
                results = [hit["_source"] for hit in response["hits"]["hits"]]
                span.set_attribute("el.hits_count", len(results))
                return results
            except NotFoundError as e:
                span.set_attribute("error", True)
                span.set_attribute("error.message", f"Объекты не найдены: {e}")
                logger.warning(f"Объекты в {table} не найдены: query={search_query}")
            except TransportError as e:
                span.set_attribute("error", True)
                span.set_attribute("error.message", f"Ошибка транспортировки: {e}")
                logger.error(f"При запросе {search_query} к {table} произошла ошибка: {e}")
            return []


async def get_elastic(request: Request) -> ElasticDAO:
    """Получение объекта ElasticSearchDB."""
    return request.app.state.elastic
