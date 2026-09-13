from api.core.sql_db import get_con
from api.rest.models.event_ticket import EventTicket
from api.dto.requests.event_ticket import CreateEventTicket, UpdateEventTicket
from api.core.utils.common import generate_sql_update_query_setter
from typing import Optional, List
from sqlite3 import DatabaseError

class EventTicketRepo:
    @staticmethod
    def get() -> List[EventTicket]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM event_ticket")
            items = cursor.fetchall()
            return items

    @staticmethod
    def get_by_id(event_ticket_id: Optional[int]) -> Optional[EventTicket]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM event_ticket WHERE id = ?", (event_ticket_id,))
            item = cursor.fetchone()
            if item:
                item = dict(item)
                return EventTicket.model_validate(item)
            return None

    @staticmethod
    def create(event_ticket: CreateEventTicket) -> Optional[EventTicket]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute(
                "INSERT INTO event_ticket(quantity_available, price, event_id, ticket_id) VALUES (?, ?, ?, ?)",
                (event_ticket.quantity_available, event_ticket.price, event_ticket.event_id, event_ticket.ticket_id)
            )
            event_ticket_id = cursor.lastrowid
            con.commit()
        return EventTicketRepo.get_by_id(event_ticket_id)

    @staticmethod
    def update_by_id(event_ticket_id: Optional[int], event_ticket: UpdateEventTicket) -> Optional[EventTicket]:
        with get_con() as con:
            cursor = con.cursor()
            set_q, vals = generate_sql_update_query_setter(event_ticket)
            if set_q is not None:
                vals.append(event_ticket_id)
                cursor.execute("UPDATE event_ticket " + set_q + " WHERE id = ?", vals)
                con.commit()
            return EventTicketRepo.get_by_id(event_ticket_id)

    @staticmethod
    def delete_by_id(event_ticket_id: Optional[int]) -> bool:
        with get_con() as con:
            cursor = con.cursor()
            try:
                cursor.execute("BEGIN")
                cursor.execute("DELETE FROM event_ticket WHERE id = ?", (event_ticket_id,))
                con.commit()
                rows = cursor.rowcount
                return rows > 0
            except DatabaseError:
                con.rollback()
                return False
