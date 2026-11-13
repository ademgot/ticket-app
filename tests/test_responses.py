from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from api.dto.responses.order import OrderResponse
from api.dto.responses.order_item import OrderItemResponse
from api.dto.responses.seat import SeatResponse
from api.dto.responses.tax_rate import TaxRateResponse
from api.dto.responses.ticket import TicketResponse
from api.dto.responses.ticket_type import TicketTypeResponse
from api.dto.responses.user import UserResponse
from api.dto.responses.venue import VenueResponse

MOMENT = datetime(2026, 11, 13, tzinfo=timezone.utc)
TIMESTAMPS = {"created_at": MOMENT, "updated_at": MOMENT}


def payload(model, **fields):
    return model.model_validate({**TIMESTAMPS, **fields})


@pytest.mark.parametrize(
    ("model", "fields", "required"),
    [
        (VenueResponse, {"id": 1, "name": "ACL Live", "timezone": "America/Chicago", "address": "310 W Willie Nelson Blvd", "state": "TX"}, "id"),
        (UserResponse, {"id": 1, "email": "ada@example.com", "name": "Ada"}, "id"),
        (SeatResponse, {"id": 1, "section": "B", "seat_row": "4", "seat_number": "12", "venue_id": 2}, "id"),
        (TicketTypeResponse, {"id": 1, "tier": "GA", "event_id": 3}, "id"),
        (TicketResponse, {"id": 1, "price": 4500, "seat_id": 2, "event_id": 3, "ticket_type_id": 4}, "id"),
        (OrderResponse, {"id": 1, "status": "paid", "user_id": 2, "subtotal": 4500, "tax_amount": 371, "total_charged": 4871, "tax_rate_applied": 0.0825, "tax_jurisdiction": "TX"}, "id"),
        (TaxRateResponse, {"id": 1, "jurisdiction": "TX", "tax_type": "sales", "rate": 0.0825, "effective_from": MOMENT}, "id"),
        (OrderItemResponse, {"order_id": 1, "ticket_id": 2}, "order_id"),
    ],
)
def test_response_accepts_a_stored_row(model, fields, required):
    response = payload(model, **fields)

    assert getattr(response, required) == fields[required]


@pytest.mark.parametrize(
    ("model", "fields", "required"),
    [
        (VenueResponse, {"id": 1, "name": "ACL Live", "timezone": "America/Chicago", "address": "310 W Willie Nelson Blvd", "state": "TX"}, "id"),
        (UserResponse, {"id": 1, "email": "ada@example.com", "name": "Ada"}, "id"),
        (SeatResponse, {"id": 1, "section": "B", "seat_row": "4", "seat_number": "12", "venue_id": 2}, "id"),
        (TicketTypeResponse, {"id": 1, "tier": "GA", "event_id": 3}, "id"),
        (TicketResponse, {"id": 1, "price": 4500, "seat_id": 2, "event_id": 3, "ticket_type_id": 4}, "id"),
        (OrderResponse, {"id": 1, "status": "paid", "user_id": 2, "subtotal": 4500, "tax_amount": 371, "total_charged": 4871, "tax_rate_applied": 0.0825, "tax_jurisdiction": "TX"}, "id"),
        (TaxRateResponse, {"id": 1, "jurisdiction": "TX", "tax_type": "sales", "rate": 0.0825, "effective_from": MOMENT}, "id"),
        (OrderItemResponse, {"order_id": 1, "ticket_id": 2}, "order_id"),
        (OrderItemResponse, {"order_id": 1, "ticket_id": 2}, "ticket_id"),
    ],
)
def test_response_requires_its_key(model, fields, required):
    body = {**TIMESTAMPS, **fields}
    del body[required]

    with pytest.raises(ValidationError):
        model.model_validate(body)


def test_ticket_response_allows_an_unsold_ticket():
    response = payload(
        TicketResponse,
        id=1,
        price=4500,
        seat_id=2,
        event_id=3,
        ticket_type_id=4,
    )

    assert response.held_until is None
    assert response.sold_at is None
    assert response.held_by_user_id is None
    assert response.sold_to_user_id is None


def test_tax_rate_response_allows_an_open_ended_rate():
    response = payload(
        TaxRateResponse,
        id=1,
        jurisdiction="TX",
        tax_type="sales",
        rate=0.0825,
        effective_from=MOMENT,
    )

    assert response.effective_to is None
