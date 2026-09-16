from api.core.sql_db import get_con
from api.rest.models.order_item import OrderItem
from api.dto.requests.order_item import CreateOrderItem
from typing import List
from sqlite3 import DatabaseError

class OrderItemRepo:
    @staticmethod
    def get() -> List[OrderItem]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM order_items")
            items = cursor.fetchall()
            return [OrderItem.model_validate(dict(item)) for item in items]

    @staticmethod
    def get_by_id(order_id: int, ticket_id: int) -> OrderItem | None:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute(
                "SELECT * FROM order_items WHERE order_id = ? AND ticket_id = ?",
                (order_id, ticket_id),
            )
            item = cursor.fetchone()
            if item:
                item = dict(item)
                return OrderItem.model_validate(item)
            return None

    @staticmethod
    def create(order_item: CreateOrderItem) -> OrderItem | None:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute(
                "INSERT INTO order_items(order_id, ticket_id) VALUES (?, ?)",
                (order_item.order_id, order_item.ticket_id),
            )
            con.commit()
        return OrderItemRepo.get_by_id(order_item.order_id, order_item.ticket_id)

    @staticmethod
    def delete_by_id(order_id: int, ticket_id: int) -> bool:
        with get_con() as con:
            cursor = con.cursor()
            try:
                cursor.execute("BEGIN")
                cursor.execute(
                    "DELETE FROM order_items WHERE order_id = ? AND ticket_id = ?",
                    (order_id, ticket_id),
                )
                con.commit()
                rows = cursor.rowcount
                return rows > 0
            except DatabaseError:
                con.rollback()
                return False
