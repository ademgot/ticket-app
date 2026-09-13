from api.core.sql_db import get_con
from api.rest.models.order import Order
from api.dto.requests.order import CreateOrder, UpdateOrder
from api.core.utils.common import generate_sql_update_query_setter
from typing import Optional, List
from sqlite3 import DatabaseError

class OrderRepo:
    @staticmethod
    def get() -> List[Order]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute('SELECT * FROM "order"')
            items = cursor.fetchall()
            return items

    @staticmethod
    def get_by_id(order_id: Optional[int]) -> Optional[Order]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute('SELECT * FROM "order" WHERE id = ?', (order_id,))
            item = cursor.fetchone()
            if item:
                item = dict(item)
                return Order.model_validate(item)
            return None

    @staticmethod
    def create(order: CreateOrder) -> Optional[Order]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute(
                'INSERT INTO "order"(status, user_id, total_price) VALUES (?, ?, ?)',
                (order.status, order.user_id, order.total_price)
            )
            order_id = cursor.lastrowid
            con.commit()
        return OrderRepo.get_by_id(order_id)

    @staticmethod
    def update_by_id(order_id: Optional[int], order: UpdateOrder) -> Optional[Order]:
        with get_con() as con:
            cursor = con.cursor()
            set_q, vals = generate_sql_update_query_setter(order)
            if set_q is not None:
                vals.append(order_id)
                cursor.execute('UPDATE "order" ' + set_q + " WHERE id = ?", vals)
                con.commit()
            return OrderRepo.get_by_id(order_id)

    @staticmethod
    def delete_by_id(order_id: Optional[int]) -> bool:
        with get_con() as con:
            cursor = con.cursor()
            try:
                cursor.execute("BEGIN")
                cursor.execute('DELETE FROM "order" WHERE id = ?', (order_id,))
                con.commit()
                rows = cursor.rowcount
                return rows > 0
            except DatabaseError:
                con.rollback()
                return False
