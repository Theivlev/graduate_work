import logging
from logging import config as logging_config

from psycopg.sql import SQL, Identifier
from utils.logger import LOGGING_CONFIG

logger = logging.getLogger(__name__)
logging_config.dictConfig(LOGGING_CONFIG)


class Query:
    """Класс SQL-запросов."""

    @staticmethod
    def get_films_query(modified_time: str) -> SQL:
        return SQL(
            """
            SELECT
                fw.id AS id,
                fw.title AS title,
                fw.description AS description,
                fw.rating AS imdb_rating,
                COALESCE(
                    jsonb_agg(
                        DISTINCT jsonb_build_object(
                            'id', p.id,
                            'full_name', p.full_name
                        )
                    ) FILTER (WHERE pfw.role = 'actor'),
                    '[]'
                ) AS actors,
                COALESCE(
                    jsonb_agg(
                        DISTINCT jsonb_build_object(
                            'id', p.id,
                            'full_name', p.full_name
                        )
                    ) FILTER (WHERE pfw.role = 'director'),
                    '[]'
                ) AS directors,
                COALESCE(
                    jsonb_agg(
                        DISTINCT jsonb_build_object(
                            'id', p.id,
                            'full_name', p.full_name
                        )
                    ) FILTER (WHERE pfw.role = 'writer'),
                    '[]'
                ) AS writers,
                COALESCE(
                    jsonb_agg(
                        DISTINCT jsonb_build_object(
                            'id', g.id,
                            'name', g.name
                        )
                    ) FILTER (WHERE g.id IS NOT NULL),
                    '[]'
                ) AS genre,
                COALESCE(array_agg(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'actor'), ARRAY[]::text[]) AS actors_names,
                COALESCE(array_agg(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'director'), ARRAY[]::text[]) AS directors_names,
                COALESCE(array_agg(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'writer'), ARRAY[]::text[]) AS writers_names,
                MAX(fw.modified) AS modified -- Добавляем MAX(fw.modified), чтобы корректно агрегировать
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            WHERE fw.modified > {last_modified}
                OR p.modified > {last_modified}
                OR g.modified > {last_modified}
            GROUP BY fw.id, fw.title, fw.description, fw.rating
            ORDER BY MAX(fw.modified)
            """
        ).format(last_modified=modified_time)

    @staticmethod
    def check_modified(table, modified_time):
        logger.info("Проверка последнего изменения для таблицы: %s с last_mod: %s", table, modified_time)

        query = SQL(
            """
                SELECT MAX(modified) AS last_modified
                FROM {table}
                WHERE modified > {last_modified}
                """
        ).format(table=Identifier("content", table), last_modified=modified_time)

        return query

    @staticmethod
    def get_genres_query(modified_time):
        return SQL(
            """
            SELECT
                g.id,
                g.name
            FROM content.genre AS g
            WHERE g.modified > {last_modified}
            ORDER BY g.modified;
            """
        ).format(last_modified=modified_time)

    @staticmethod
    def get_persons_query(modified_time):
        return SQL(
            """
            WITH person_roles AS (SELECT pfw.person_id,
                                         pfw.film_work_id,
                                         COALESCE(
                                                 jsonb_agg(
                                                         pfw.role
                                                     ),
                                                 '[]'::jsonb
                                             ) AS roles
                                  FROM content.person_film_work AS pfw
                                  GROUP BY pfw.person_id, pfw.film_work_id)
            SELECT p.id,
                   p.full_name,
                   COALESCE(
                                   jsonb_agg(
                                   jsonb_build_object(
                                           'id', person_roles.film_work_id,
                                           'roles', person_roles.roles
                                       )
                               ) FILTER (WHERE p.id IS NOT NULL),
                                   '[]'::jsonb
                       ) AS films
            FROM content.person AS p
                     LEFT JOIN person_roles ON person_roles.person_id = p.id
            WHERE p.modified > {last_modified}
            GROUP BY p.id, p.full_name
            ORDER BY MAX(p.modified);
            """
        ).format(last_modified=modified_time)
