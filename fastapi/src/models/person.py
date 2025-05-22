from typing import List

from pydantic import Field

from .mixins import UUIDMixin


class FilmDTO(UUIDMixin):
    """Модель фильма."""

    roles: List[str] = Field(default_factory=list)


class PersonDTO(UUIDMixin):
    """Модель информации о человеке."""

    full_name: str = Field(default_factory=str, examples=["Garry Wayne"])


class PersonInfoDTO(PersonDTO):
    """Модель информации о человеке с фильмами."""

    films: List[FilmDTO] = Field(default_factory=list)
