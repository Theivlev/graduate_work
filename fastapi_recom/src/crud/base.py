# app/crud/base.py
from typing import Optional
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User


class CRUDBase:
    """
    Базовый класс для CRUD (Create, Read, Update, Delete) операций с базой данных.
    """

    def __init__(self, model):
        self.model = model

    async def get(self, obj_id: UUID, session: AsyncSession):
        db_obj = await session.execute(self.get_query().where(self.model.id == obj_id))
        return db_obj.scalars().first()

    async def get_multi(self, session: AsyncSession, obj_id: UUID = None):
        db_objs = await session.execute(self.get_query())
        return db_objs.scalars().all()

    async def create(self, obj_in, session: AsyncSession, user: Optional[User] = None):
        obj_in_data = obj_in.dict()
        if user is not None:
            obj_in_data["user_id"] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    @staticmethod
    async def update(db_obj, obj_in, session: AsyncSession):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    @staticmethod
    async def remove(db_obj, session: AsyncSession):
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    def get_query(self):
        return select(self.model)
