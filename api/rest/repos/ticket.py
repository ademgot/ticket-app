from api.core.sql_db import get_con
from api.rest.models.ticket import Ticket
from api.rest.repos.base import BaseRepo
from api.dto.requests.ticket import CreateTicket, UpdateTicket
from api.dto.requests.pagination import Pagination
from api.dto.responses.page import Page
from api.dto.responses.ticket import TicketResponse
from api.core.utils.common import generate_sql_update_query_setter
from typing import Optional
from sqlite3 import DatabaseError

class TicketRepo:
    @staticmethod
    def get(pagination: Pagination) -> Page[TicketResponse]:
        rows, total = BaseRepo.get_page("tickets", pagination)
        return Page(
            items=[TicketResponse.model_validate(row) for row in rows],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    @staticmethod
    def get_by_id(ticket_id: Optional[int]) -> Optional[Ticket]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM tickets WHERE id = %s", (ticket_id,))
            item = cursor.fetchone()
            if item:
                item = dict(item)
                return Ticket.model_validate(item)
            return None

    @staticmethod
    def create(ticket: CreateTicket) -> Optional[Ticket]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute(
                """
                INSERT INTO tickets(price, seat_id, event_id, ticket_type_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (
                    ticket.price,
                    ticket.seat_id,
                    ticket.event_id,
                    ticket.ticket_type_id,
                ),
            )
            ticket_id = cursor.fetchone()["id"]
            con.commit()
        return TicketRepo.get_by_id(ticket_id)

    @staticmethod
    def update_by_id(ticket_id: Optional[int], ticket: UpdateTicket) -> Optional[Ticket]:
        with get_con() as con:
            cursor = con.cursor()
            set_q, vals = generate_sql_update_query_setter(ticket)
            if set_q is not None:
                vals.append(ticket_id)
                cursor.execute("UPDATE tickets " + set_q + " WHERE id = %s", vals)
                con.commit()
            return TicketRepo.get_by_id(ticket_id)

    @staticmethod
    def delete_by_id(ticket_id: Optional[int]) -> bool:
        with get_con() as con:
            cursor = con.cursor()
            try:
                cursor.execute("BEGIN")
                cursor.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
                con.commit()
                rows = cursor.rowcount
                return rows > 0
            except DatabaseError:
                con.rollback()
                return False
