from sqlite3 import DatabaseError

from api.core.sql_db import get_con
from api.core.utils.common import generate_sql_update_query_setter
from api.dto.requests.ticket_type import CreateTicketType, UpdateTicketType
from api.rest.models.ticket_type import TicketType


class TicketTypeRepo:
    @staticmethod
    def get() -> list[TicketType]:
        with get_con() as con:
            items = con.execute("SELECT * FROM ticket_types").fetchall()
            return [TicketType.model_validate(dict(item)) for item in items]

    @staticmethod
    def get_by_id(ticket_type_id: int | None) -> TicketType | None:
        with get_con() as con:
            item = con.execute(
                "SELECT * FROM ticket_types WHERE id = ?", (ticket_type_id,)
            ).fetchone()
            return TicketType.model_validate(dict(item)) if item else None

    @staticmethod
    def create(ticket_type: CreateTicketType) -> TicketType | None:
        with get_con() as con:
            cursor = con.execute(
                "INSERT INTO ticket_types(tier, event_id) VALUES (?, ?)",
                (ticket_type.tier, ticket_type.event_id),
            )
            ticket_type_id = cursor.lastrowid
            con.commit()
        return TicketTypeRepo.get_by_id(ticket_type_id)

    @staticmethod
    def update_by_id(
        ticket_type_id: int, ticket_type: UpdateTicketType
    ) -> TicketType | None:
        with get_con() as con:
            set_q, vals = generate_sql_update_query_setter(ticket_type)
            if set_q is not None:
                vals.append(ticket_type_id)
                con.execute(
                    "UPDATE ticket_types " + set_q + " WHERE id = ?", vals
                )
                con.commit()
        return TicketTypeRepo.get_by_id(ticket_type_id)

    @staticmethod
    def delete_by_id(ticket_type_id: int) -> bool:
        with get_con() as con:
            try:
                cursor = con.execute(
                    "DELETE FROM ticket_types WHERE id = ?", (ticket_type_id,)
                )
                con.commit()
                return cursor.rowcount > 0
            except DatabaseError:
                con.rollback()
                return False
