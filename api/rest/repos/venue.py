from api.core.sql_db import get_con
from api.rest.models.venue import Venue
from api.dto.requests.venue import CreateVenue, UpdateVenue
from api.core.utils.common import generate_sql_update_query_setter
from typing import Optional, List
from sqlite3 import DatabaseError

class VenueRepo:
    @staticmethod
    def get() -> List[Venue]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM venues")
            items = cursor.fetchall()
            return [Venue.model_validate(dict(item)) for item in items]

    @staticmethod
    def get_by_id(venue_id: Optional[int]) -> Optional[Venue]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM venues WHERE id = %s", (venue_id,))
            item = cursor.fetchone()
            if item:
                item = dict(item)
                return Venue.model_validate(item)
            return None

    @staticmethod
    def create(venue: CreateVenue) -> Optional[Venue]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute(
                """
                INSERT INTO venues(name, timezone, address)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (venue.name, venue.timezone, venue.address),
            )
            venue_id = cursor.fetchone()["id"]
            con.commit()
        return VenueRepo.get_by_id(venue_id)

    @staticmethod
    def update_by_id(venue_id: Optional[int], venue: UpdateVenue) -> Optional[Venue]:
        with get_con() as con:
            cursor = con.cursor()
            set_q, vals = generate_sql_update_query_setter(venue)
            if set_q is not None:
                vals.append(venue_id)
                cursor.execute("UPDATE venues " + set_q + " WHERE id = %s", vals)
                con.commit()
            return VenueRepo.get_by_id(venue_id)

    @staticmethod
    def delete_by_id(venue_id: Optional[int]) -> bool:
        with get_con() as con:
            cursor = con.cursor()
            try:
                cursor.execute("BEGIN")
                cursor.execute("DELETE FROM venues WHERE id = %s", (venue_id,))
                con.commit()
                rows = cursor.rowcount
                return rows > 0
            except DatabaseError:
                con.rollback()
                return False
