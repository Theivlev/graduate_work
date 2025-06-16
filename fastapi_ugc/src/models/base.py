import re

from beanie import Document


class BaseDocument(Document):
    """Базовый класс для документов."""

    @classmethod
    def get_name(cls):
        """Возвращает имя документа в формате snake_case."""
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
