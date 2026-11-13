from contextlib import contextmanager
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from psycopg import sql

from api.dto.requests.pagination import Pagination
from api.rest.repos.order import OrderRepo
from api.rest.repos.order_item import OrderItemRepo
from api.rest.repos.seat import SeatRepo
from api.rest.repos.tax_rate import TaxRateRepo
from api.rest.repos.ticket import TicketRepo
from api.rest.repos.ticket_type import TicketTypeRepo
from api.rest.repos.user import UserRepo
from api.rest.repos.venue import VenueRepo
from api.rest.routers import order as order_router
from api.rest.routers import order_item as order_item_router
from api.rest.routers import seat as seat_router
from api.rest.routers import tax_rate as tax_rate_router
from api.rest.routers import ticket as ticket_router
from api.rest.routers import ticket_type as ticket_type_router
from api.rest.routers import user as user_router
from api.rest.routers import venue as venue_router

MOMENT = datetime(2026, 11, 13, tzinfo=timezone.utc)
STAMPS = {"created_at": MOMENT, "updated_at": MOMENT}


def render_sql(query) -> str:
    if isinstance(query, sql.Composed):
        return "".join(render_sql(part) for part in query)
    obj = query._obj
    if isinstance(obj, tuple):
        return ".".join(obj)
    return obj


def fake_con(rows, total=0):
    cursor = MagicMock()
    cursor.fetchall.return_value = rows
    cursor.fetchone.return_value = {"total": total}
    con = MagicMock()
    con.cursor.return_value = cursor
    fake_con.cursor = cursor

    @contextmanager
    def manager():
        yield con

    return manager()


LISTS = [
    (
        UserRepo,
        user_router.get,
        "users",
        "ORDER BY id",
        {**STAMPS, "id": 1, "email": "ada@example.com", "name": "Ada", "_total": 8},
        "email",
        "ada@example.com",
    ),
    (
        VenueRepo,
        venue_router.get,
        "venues",
        "ORDER BY id",
        {
            **STAMPS,
            "id": 2,
            "name": "ACL Live",
            "timezone": "America/Chicago",
            "address": "310 W Willie Nelson Blvd",
            "state": "TX",
            "_total": 8,
        },
        "name",
        "ACL Live",
    ),
    (
        SeatRepo,
        seat_router.get,
        "seats",
        "ORDER BY id",
        {**STAMPS, "id": 3, "section": "B", "seat_row": "4", "seat_number": "12", "venue_id": 2, "_total": 8},
        "section",
        "B",
    ),
    (
        TicketTypeRepo,
        ticket_type_router.get,
        "ticket_types",
        "ORDER BY id",
        {**STAMPS, "id": 4, "tier": "GA", "event_id": 3, "_total": 8},
        "tier",
        "GA",
    ),
    (
        TicketRepo,
        ticket_router.get,
        "tickets",
        "ORDER BY id",
        {**STAMPS, "id": 5, "price": 4500, "seat_id": 2, "event_id": 3, "ticket_type_id": 4, "_total": 8},
        "price",
        4500,
    ),
    (
        OrderRepo,
        order_router.get,
        "orders",
        "ORDER BY id",
        {
            **STAMPS,
            "id": 6,
            "status": "paid",
            "user_id": 1,
            "subtotal": 4500,
            "tax_amount": 371,
            "total_charged": 4871,
            "tax_rate_applied": 0.0825,
            "tax_jurisdiction": "TX",
            "_total": 8,
        },
        "status",
        "paid",
    ),
    (
        OrderItemRepo,
        order_item_router.get,
        "order_items",
        "ORDER BY order_id, ticket_id",
        {**STAMPS, "order_id": 6, "ticket_id": 5, "_total": 8},
        "ticket_id",
        5,
    ),
    (
        TaxRateRepo,
        tax_rate_router.get,
        "tax_rates",
        "ORDER BY id",
        {
            **STAMPS,
            "id": 7,
            "jurisdiction": "TX",
            "tax_type": "sales",
            "rate": 0.0825,
            "effective_from": MOMENT,
            "_total": 8,
        },
        "jurisdiction",
        "TX",
    ),
]


@pytest.mark.parametrize(
    ("repo", "route", "table", "order", "row", "field", "value"),
    LISTS,
)
def test_list_returns_one_ordered_page(repo, route, table, order, row, field, value):
    with patch("api.rest.repos.base.get_con", side_effect=lambda: fake_con([row])):
        page = repo.get(Pagination(page=2, page_size=1))
        query, params = fake_con.cursor.execute.call_args.args
        routed = route(Pagination(page=2, page_size=1))

    assert page.total == 8
    assert page.page == 2
    assert page.page_size == 1
    assert getattr(page.items[0], field) == value
    assert routed.total == 8
    assert getattr(routed.items[0], field) == value
    assert params == (1, 1)
    statement = render_sql(query)
    assert f"FROM {table}" in statement
    assert order in statement
    assert "_total" not in page.items[0].model_dump()
