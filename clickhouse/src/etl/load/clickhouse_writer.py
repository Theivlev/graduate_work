import logging
from dataclasses import dataclass
from typing import List

from aiochclient import ChClient
from aiohttp import ClientSession
from core.base import BaseWriter
from core.config import settings
from models.message import MessageDTO

from .query import QueryBuilder


@dataclass
class ClickHouseWriter(BaseWriter):
    session: ClientSession = None
    client: ChClient = None
    query_builder: QueryBuilder = QueryBuilder()

    async def __aenter__(self):
        self.session = ClientSession()
        self.client = ChClient(self.session, settings.clickhouse_nodes[0])
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def write(self, rows: List[MessageDTO]):
        try:
            query = self.query_builder.build_insert_query(
                table_name="data_analytics.event_table", model_class=MessageDTO
            )
            await self.client.execute(query, *rows)
            logging.info("Данные успешно записаны в ClickHouse.")
        except Exception as e:
            logging.error(f"Ошибка при записи данных в ClickHouse: {e}")
            raise
