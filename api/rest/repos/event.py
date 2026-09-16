from api.core.sql_db import get_con
from api.rest.models.event import Event
from api.dto.requests.event import CreateEvent, UpdateEvent
from api.core.utils.common import generate_sql_update_query_setter
from typing import Optional, List
from sqlite3 import DatabaseError

class EventRepo:
    @staticmethod
    def get() -> List[Event]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM events")
            items = cursor.fetchall()
            return [Event.model_validate(dict(item)) for item in items]

    @staticmethod
    def get_by_id(event_id: Optional[int]) -> Optional[Event]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
            item = cursor.fetchone()
            if item:
                item = dict(item)
                return Event.model_validate(item)
            return None

    @staticmethod
    def create(event: CreateEvent) -> Optional[Event]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute(
                "INSERT INTO events(name, venue_id, starts_at, ends_at) VALUES (?, ?, ?, ?)",
                (event.name, event.venue_id, event.starts_at, event.ends_at),
            )
            event_id = cursor.lastrowid
            con.commit()
        return EventRepo.get_by_id(event_id)

    @staticmethod
    def update_by_id(event_id: Optional[int], event: UpdateEvent) -> Optional[Event]:
        with get_con() as con:
            cursor = con.cursor()
            set_q, vals = generate_sql_update_query_setter(event)
            if set_q is not None:
                vals.append(event_id)
                cursor.execute("UPDATE events " + set_q + " WHERE id = ?", vals)
                con.commit()
            return EventRepo.get_by_id(event_id)

    @staticmethod
    def delete_by_id(event_id: Optional[int]) -> bool:
        with get_con() as con:
            cursor = con.cursor()
            try:
                cursor.execute("BEGIN")
                cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
                con.commit()
                rows = cursor.rowcount
                return rows > 0
            except DatabaseError:
                con.rollback()
                return False
