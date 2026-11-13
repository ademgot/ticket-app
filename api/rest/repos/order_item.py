from api.core.sql_db import get_con
from api.rest.models.order_item import OrderItem
from api.rest.repos.base import BaseRepo
from api.dto.requests.order_item import CreateOrderItem
from api.dto.requests.pagination import Pagination
from api.dto.responses.order_item import OrderItemResponse
from api.dto.responses.page import Page
from sqlite3 import DatabaseError

class OrderItemRepo:
    @staticmethod
    def get(pagination: Pagination) -> Page[OrderItemResponse]:
        rows, total = BaseRepo.get_page(
            "order_items",
            pagination,
            order_by=("order_id", "ticket_id"),
        )
        return Page(
            items=[OrderItemResponse.model_validate(row) for row in rows],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    @staticmethod
    def get_by_id(order_id: int, ticket_id: int) -> OrderItem | None:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute(
                "SELECT * FROM order_items WHERE order_id = %s AND ticket_id = %s",
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
                "INSERT INTO order_items(order_id, ticket_id) VALUES (%s, %s)",
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
                    "DELETE FROM order_items WHERE order_id = %s AND ticket_id = %s",
                    (order_id, ticket_id),
                )
                con.commit()
                rows = cursor.rowcount
                return rows > 0
            except DatabaseError:
                con.rollback()
                return False
