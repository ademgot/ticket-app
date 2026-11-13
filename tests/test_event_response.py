from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from api.dto.responses.event import EventResponse


def event_payload(**overrides):
    moment = datetime(2026, 11, 13, tzinfo=timezone.utc)
    payload = {
        "id": 1,
        "name": "ACL Studio Session",
        "venue_id": 2,
        "starts_at": moment,
        "ends_at": moment,
        "created_at": moment,
        "updated_at": moment,
    }
    payload.update(overrides)
    return payload


def test_event_response_accepts_a_stored_event():
    response = EventResponse.model_validate(event_payload())

    assert response.id == 1
    assert response.name == "ACL Studio Session"
    assert response.venue_id == 2


def test_event_response_requires_id():
    payload = event_payload()
    del payload["id"]

    with pytest.raises(ValidationError):
        EventResponse.model_validate(payload)
