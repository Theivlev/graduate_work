import orjson


def orjson_dumps(v, *, default):
    """Функция для быстрой сериализации JSON с помощью orjson."""
    return orjson.dumps(v, default=default).decode()
