from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.crud.base import CRUDBase
from src.models.user import User


class UserCrud(CRUDBase):
    def get_query(self):
        return select(self.model).options(selectinload(User.roles))
