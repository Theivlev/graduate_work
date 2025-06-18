from beanie import Document
from pydantic import Field
from src.models.mixins import PyObjectId


class MovieViewStats(Document):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    watched_count: int
    movies_in_category: int
    genre: str

    class Settings:
        name = "movie_view_stats"
