from sqlite3 import DatabaseError

from api.core.sql_db import get_con
from api.core.utils.common import generate_sql_update_query_setter
from api.dto.requests.seat import CreateSeat, UpdateSeat
from api.rest.models.seat import Seat


class SeatRepo:
    @staticmethod
    def get() -> list[Seat]:
        with get_con() as con:
            items = con.execute("SELECT * FROM seats").fetchall()
            return [Seat.model_validate(dict(item)) for item in items]

    @staticmethod
    def get_by_id(seat_id: int | None) -> Seat | None:
        with get_con() as con:
            item = con.execute("SELECT * FROM seats WHERE id = %s", (seat_id,)).fetchone()
            return Seat.model_validate(dict(item)) if item else None

    @staticmethod
    def create(seat: CreateSeat) -> Seat | None:
        with get_con() as con:
            cursor = con.execute(
                """
                INSERT INTO seats(section, seat_row, seat_number, venue_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (seat.section, seat.seat_row, seat.seat_number, seat.venue_id),
            )
            seat_id = cursor.fetchone()["id"]
            con.commit()
        return SeatRepo.get_by_id(seat_id)

    @staticmethod
    def update_by_id(seat_id: int, seat: UpdateSeat) -> Seat | None:
        with get_con() as con:
            set_q, vals = generate_sql_update_query_setter(seat)
            if set_q is not None:
                vals.append(seat_id)
                con.execute("UPDATE seats " + set_q + " WHERE id = %s", vals)
                con.commit()
        return SeatRepo.get_by_id(seat_id)

    @staticmethod
    def delete_by_id(seat_id: int) -> bool:
        with get_con() as con:
            try:
                cursor = con.execute("DELETE FROM seats WHERE id = %s", (seat_id,))
                con.commit()
                return cursor.rowcount > 0
            except DatabaseError:
                con.rollback()
                return False
