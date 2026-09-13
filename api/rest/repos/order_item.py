from api.core.sql_db import get_con
from api.rest.models.order_item import OrderItem
from api.dto.requests.order_item import CreateOrderItem, UpdateOrderItem
from api.core.utils.common import generate_sql_update_query_setter
from typing import Optional, List
from sqlite3 import DatabaseError

class OrderItemRepo:
    @staticmethod
    def get() -> List[OrderItem]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM order_item")
            items = cursor.fetchall()
            return items

    @staticmethod
    def get_by_id(order_item_id: Optional[int]) -> Optional[OrderItem]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM order_item WHERE id = ?", (order_item_id,))
            item = cursor.fetchone()
            if item:
                item = dict(item)
                return OrderItem.model_validate(item)
            return None

    @staticmethod
    def create(order_item: CreateOrderItem) -> Optional[OrderItem]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute(
                "INSERT INTO order_item(quantity, order_id, event_ticket_id, price_paid) VALUES (?, ?, ?, ?)",
                (order_item.quantity, order_item.order_id, order_item.event_ticket_id, order_item.price_paid)
            )
            order_item_id = cursor.lastrowid
            con.commit()
        return OrderItemRepo.get_by_id(order_item_id)

    @staticmethod
    def update_by_id(order_item_id: Optional[int], order_item: UpdateOrderItem) -> Optional[OrderItem]:
        with get_con() as con:
            cursor = con.cursor()
            set_q, vals = generate_sql_update_query_setter(order_item)
            if set_q is not None:
                vals.append(order_item_id)
                cursor.execute("UPDATE order_item " + set_q + " WHERE id = ?", vals)
                con.commit()
            return OrderItemRepo.get_by_id(order_item_id)

    @staticmethod
    def delete_by_id(order_item_id: Optional[int]) -> bool:
        with get_con() as con:
            cursor = con.cursor()
            try:
                cursor.execute("BEGIN")
                cursor.execute("DELETE FROM order_item WHERE id = ?", (order_item_id,))
                con.commit()
                rows = cursor.rowcount
                return rows > 0
            except DatabaseError:
                con.rollback()
                return False
