from pydantic import Field

from .genre import MoviesGenreDTO
from .mixins import UUIDMixin


class MovieDTO(UUIDMixin):
    """Модель фильма"""

    imdb_rating: float | None = Field(default=None)
    genre: list[MoviesGenreDTO] = Field(default_factory=list)
    title: str
    description: str | None = Field(default=None)
    directors_names: str | list[str] | None = Field(default_factory=list)
    actors_names: str | list[str] | None = Field(default_factory=list)
    writers_names: str | list[str] | None = Field(default_factory=list)
    directors: list[dict] | None = Field(default_factory=list)
    actors: list[dict] = Field(default_factory=list)
    writers: list[dict] = Field(default_factory=list)
