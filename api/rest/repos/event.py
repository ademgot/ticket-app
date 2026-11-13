from api.core.sql_db import get_con
from api.rest.models.event import Event
from api.dto.requests.event import CreateEvent, EventListFilters, UpdateEvent
from api.dto.requests.pagination import Pagination
from api.dto.responses.event import EventResponse
from api.dto.responses.page import Page
from api.core.utils.common import generate_sql_update_query_setter
from typing import Optional
from sqlite3 import DatabaseError
from psycopg import sql


def _like(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _event_where(filters: EventListFilters | None) -> tuple[sql.Composable, list]:
    filters = filters or EventListFilters()
    clauses: list[sql.Composable] = []
    params: list = []
    if filters.q:
        clauses.append(
            sql.SQL(
                "(events.name ILIKE %s ESCAPE '\\' OR venues.name ILIKE %s ESCAPE '\\')"
            )
        )
        pattern = _like(filters.q)
        params.extend([pattern, pattern])
    if filters.location:
        clauses.append(
            sql.SQL(
                "(venues.address ILIKE %s ESCAPE '\\' OR venues.state ILIKE %s ESCAPE '\\')"
            )
        )
        pattern = _like(filters.location)
        params.extend([pattern, pattern])
    if filters.starts_after is not None:
        clauses.append(sql.SQL("events.starts_at >= %s"))
        params.append(filters.starts_after)
    if filters.starts_before is not None:
        clauses.append(sql.SQL("events.starts_at < %s"))
        params.append(filters.starts_before)
    if not clauses:
        return sql.SQL(""), params
    return sql.SQL(" WHERE ") + sql.SQL(" AND ").join(clauses), params


class EventRepo:
    @staticmethod
    def get(
        pagination: Pagination,
        filters: EventListFilters | None = None,
    ) -> Page[EventResponse]:
        where, params = _event_where(filters)
        query = sql.SQL(
            """
            SELECT events.*, venues.name AS venue_name, COUNT(*) OVER() AS _total
            FROM events
            JOIN venues ON venues.id = events.venue_id
            {where}
            ORDER BY events.id
            LIMIT %s OFFSET %s
            """
        ).format(where=where)
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute(query, [*params, pagination.page_size, pagination.offset])
            rows = cursor.fetchall()
            if rows:
                total = int(rows[0]["_total"])
                items = [
                    {key: value for key, value in dict(row).items() if key != "_total"}
                    for row in rows
                ]
            else:
                count = sql.SQL(
                    """
                    SELECT COUNT(*) AS total
                    FROM events
                    JOIN venues ON venues.id = events.venue_id
                    {where}
                    """
                ).format(where=where)
                cursor.execute(count, params)
                total = int(cursor.fetchone()["total"])
                items = []
        return Page(
            items=[EventResponse.model_validate(row) for row in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    @staticmethod
    def get_by_id(event_id: Optional[int]) -> Optional[Event]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
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
                """
                INSERT INTO events(name, venue_id, starts_at, ends_at)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (event.name, event.venue_id, event.starts_at, event.ends_at),
            )
            event_id = cursor.fetchone()["id"]
            con.commit()
        return EventRepo.get_by_id(event_id)

    @staticmethod
    def update_by_id(event_id: Optional[int], event: UpdateEvent) -> Optional[Event]:
        with get_con() as con:
            cursor = con.cursor()
            set_q, vals = generate_sql_update_query_setter(event)
            if set_q is not None:
                vals.append(event_id)
                cursor.execute("UPDATE events " + set_q + " WHERE id = %s", vals)
                con.commit()
            return EventRepo.get_by_id(event_id)

    @staticmethod
    def delete_by_id(event_id: Optional[int]) -> bool:
        with get_con() as con:
            cursor = con.cursor()
            try:
                cursor.execute("BEGIN")
                cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
                con.commit()
                rows = cursor.rowcount
                return rows > 0
            except DatabaseError:
                con.rollback()
                return False
