from uuid import UUID

from beanie import Document
from pydantic import Field
from src.models.mixins import PyObjectId


class User(Document):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: UUID
    first_name: str
    last_name: str | None
    email: str
    tg_id: str | None
    phone_numer: str | None

    class Settings:
        name = "users"
