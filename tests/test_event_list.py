from contextlib import contextmanager
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from psycopg import sql

from api.dto.requests.pagination import Pagination
from api.rest.repos.event import EventRepo
from api.rest.routers.event import get

MOMENT = datetime(2026, 11, 13, tzinfo=timezone.utc)


def render_sql(query) -> str:
    if isinstance(query, sql.Composed):
        return "".join(render_sql(part) for part in query)
    obj = query._obj
    if isinstance(obj, tuple):
        return ".".join(obj)
    return obj


def event_row(**overrides):
    row = {
        "id": 1,
        "name": "ACL Studio Session",
        "venue_id": 2,
        "starts_at": MOMENT,
        "ends_at": MOMENT,
        "created_at": MOMENT,
        "updated_at": MOMENT,
        "_total": 12,
    }
    row.update(overrides)
    return row


@contextmanager
def connection(rows, total=0):
    cursor = MagicMock()
    cursor.fetchall.return_value = rows
    cursor.fetchone.return_value = {"total": total}
    con = MagicMock()
    con.cursor.return_value = cursor
    connection.cursor = cursor
    yield con


def test_event_repo_get_returns_one_ordered_page():
    with patch("api.rest.repos.base.get_con", return_value=connection([event_row()])):
        page = EventRepo.get(Pagination(page=2, page_size=1))

    assert page.total == 12
    assert page.page == 2
    assert page.page_size == 1
    assert page.items[0].id == 1
    assert page.items[0].name == "ACL Studio Session"
    query, params = connection.cursor.execute.call_args.args
    assert params == (1, 1)
    statement = render_sql(query)
    assert "FROM events" in statement
    assert "ORDER BY id" in statement
    assert "LIMIT %s OFFSET %s" in statement
    assert "_total" not in page.items[0].model_dump()


def test_event_repo_get_counts_when_the_page_is_empty():
    with patch("api.rest.repos.base.get_con", return_value=connection([], total=4)):
        page = EventRepo.get(Pagination(page=3, page_size=50))

    assert page.items == []
    assert page.total == 4
    assert connection.cursor.execute.call_count == 2
    count_query = connection.cursor.execute.call_args_list[1].args[0]
    assert render_sql(count_query) == "SELECT COUNT(*) AS total FROM events"


def test_list_events_returns_the_page():
    row = event_row(_total=3)
    with patch("api.rest.repos.base.get_con", return_value=connection([row])):
        page = get(Pagination(page=2, page_size=1))

    assert page.total == 3
    assert page.page == 2
    assert page.page_size == 1
    assert page.items[0].name == "ACL Studio Session"
