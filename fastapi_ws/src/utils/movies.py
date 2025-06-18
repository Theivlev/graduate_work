from uuid import UUID

from asyncpg import connect
from src.core.config import postgres_settings
from src.schemas.film_schema import MovieBaseDTO


async def get_movie_by_id(movie_id: UUID):
    conn = await connect(
        host=postgres_settings.host,
        port=postgres_settings.port,
        user=postgres_settings.user,
        password=postgres_settings.password,
        database=postgres_settings.name,
    )
    try:
        row = await conn.fetchrow("SELECT id, title FROM content.film_work WHERE id = $1", movie_id)
        if not row:
            return None
        return MovieBaseDTO(**dict(row))
    finally:
        await conn.close()
