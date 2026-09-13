from api.core.sql_db import get_con
from api.rest.models.ticket import Ticket
from api.dto.requests.ticket import CreateTicket, UpdateTicket
from api.core.utils.common import generate_sql_update_query_setter
from typing import Optional, List
from sqlite3 import DatabaseError

class TicketRepo:
    @staticmethod
    def get() -> List[Ticket]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM ticket")
            items = cursor.fetchall()
            return items

    @staticmethod
    def get_by_id(ticket_id: Optional[int]) -> Optional[Ticket]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM ticket WHERE id = ?", (ticket_id,))
            item = cursor.fetchone()
            if item:
                item = dict(item)
                return Ticket.model_validate(item)
            return None

    @staticmethod
    def create(ticket: CreateTicket) -> Optional[Ticket]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute("INSERT INTO ticket(tier) VALUES (?)", (ticket.tier,))
            ticket_id = cursor.lastrowid
            con.commit()
        return TicketRepo.get_by_id(ticket_id)

    @staticmethod
    def update_by_id(ticket_id: Optional[int], ticket: UpdateTicket) -> Optional[Ticket]:
        with get_con() as con:
            cursor = con.cursor()
            set_q, vals = generate_sql_update_query_setter(ticket)
            if set_q is not None:
                vals.append(ticket_id)
                cursor.execute("UPDATE ticket " + set_q + " WHERE id = ?", vals)
                con.commit()
            return TicketRepo.get_by_id(ticket_id)

    @staticmethod
    def delete_by_id(ticket_id: Optional[int]) -> bool:
        with get_con() as con:
            cursor = con.cursor()
            try:
                cursor.execute("BEGIN")
                cursor.execute("DELETE FROM ticket WHERE id = ?", (ticket_id,))
                con.commit()
                rows = cursor.rowcount
                return rows > 0
            except DatabaseError:
                con.rollback()
                return False
