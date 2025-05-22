from typing import Any, List, Type


class QueryBuilder:
    @staticmethod
    def build_insert_query(table_name: str, model_class: Type[Any]) -> str:
        """
        Формирует SQL-запрос для вставки данных в таблицу.
        """
        columns = ", ".join(model_class.__annotations__.keys())
        return f"INSERT INTO {table_name} ({columns}) VALUES"

    @staticmethod
    def build_select_query(table_name: str, columns: List[str] = None) -> str:
        """
        Формирует SQL-запрос для выборки данных из таблицы.
        """
        if columns is None:
            columns = ["*"]
        columns_str = ", ".join(columns)
        return f"SELECT {columns_str} FROM {table_name}"

    @staticmethod
    def build_update_query(table_name: str, set_columns: List[str], where_clause: str = None) -> str:
        """
        Формирует SQL-запрос для обновления данных в таблице.
        """
        set_clause = ", ".join([f"{col} = ?" for col in set_columns])
        query = f"UPDATE {table_name} SET {set_clause}"
        if where_clause:
            query += f" WHERE {where_clause}"
        return query

    @staticmethod
    def build_delete_query(table_name: str, where_clause: str = None) -> str:
        """
        Формирует SQL-запрос для удаления данных из таблицы.
        """
        query = f"DELETE FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        return query
