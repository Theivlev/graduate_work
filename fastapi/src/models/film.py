from pydantic import Field

from .genre import GenreDTO
from .mixins import UUIDMixin
from .person import PersonDTO


class MovieBaseDTO(UUIDMixin):
    """Базовая информация о фильме."""

    title: str = Field(examples=["The Star"])
    imdb_rating: float | None = Field(default=None, examples=[8.5])


class MovieInfoDTO(MovieBaseDTO):
    """Модель фильма"""

    description: str | None = Field(default=None, examples=["New World"])
    genre: list[GenreDTO] = Field(default_factory=list)
    actors: list[PersonDTO] = Field(default_factory=list)
    writers: list[PersonDTO] = Field(default_factory=list)
    directors: list[PersonDTO] | None = Field(default_factory=list)
