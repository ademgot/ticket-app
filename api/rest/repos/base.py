from api.core.sql_db import get_con
from api.dto.requests.pagination import Pagination
from psycopg import sql


class BaseRepo:
    @staticmethod
    def get(table_name: str):
        with get_con() as con:
            cursor = con.cursor()
            query = sql.SQL("SELECT * FROM {table_name}").format(table_name=sql.Identifier(table_name))
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def get_page(
        table_name: str,
        pagination: Pagination,
        order_by: tuple[str, ...] = ("id",),
    ) -> tuple[list[dict], int]:
        order = sql.SQL(", ").join(sql.Identifier(column) for column in order_by)
        query = sql.SQL(
            """
            SELECT *, COUNT(*) OVER() AS _total
            FROM {table_name}
            ORDER BY {order_by}
            LIMIT %s OFFSET %s
            """
        ).format(table_name=sql.Identifier(table_name), order_by=order)
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute(query, (pagination.page_size, pagination.offset))
            rows = cursor.fetchall()
            if rows:
                total = int(rows[0]["_total"])
                items = [
                    {key: value for key, value in dict(row).items() if key != "_total"}
                    for row in rows
                ]
                return items, total
            count = sql.SQL("SELECT COUNT(*) AS total FROM {table_name}").format(
                table_name=sql.Identifier(table_name)
            )
            cursor.execute(count)
            return [], int(cursor.fetchone()["total"])