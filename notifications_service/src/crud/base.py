from typing import Generic, List, Optional, Type, TypeVar

from beanie import Document
from bson import ObjectId

ModelType = TypeVar("ModelType", bound=Document)


class BaseMongoCRUD(Generic[ModelType]):
    """
    Базовый CRUD-класс для работы с Beanie моделями.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Инициализация CRUD-сервиса.
        """
        self.model = model

    async def create(self, data: dict) -> ModelType:
        """
        Создает новый документ в коллекции.
        """
        document = self.model(**data)
        await document.insert()
        return document

    async def get(self, id_: str) -> Optional[ModelType]:
        """
        Получает документ по ID.
        """
        return await self.model.get(ObjectId(id_))

    async def find(self, filter_: dict, page_number: int = 0, page_size: int = 10) -> List[ModelType]:
        """
        Ищет документы с пагинацией.
        """
        skip = page_number * page_size
        return await self.model.find(filter_).skip(skip).limit(page_size).to_list()

    async def find_one(self, filter_: dict) -> ModelType:
        """ "Поиск одного документа по заданному фильтру"""
        return await self.model.find_one(filter_)

    async def update(self, id_: str, data: dict) -> Optional[ModelType]:
        """
        Обновляет документ по ID.
        """
        document = await self.model.get(ObjectId(id_))
        if document:
            await document.set(data)
        return document

    async def delete(self, id_: str) -> bool:
        """
        Удаляет документ по ID.
        """
        document = await self.model.get(ObjectId(id_))
        if document:
            await document.delete()
            return True
        return False
