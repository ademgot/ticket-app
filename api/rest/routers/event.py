from datetime import datetime

from fastapi import APIRouter, Depends, Query
from api.dto.requests.event import CreateEvent, EventListFilters, UpdateEvent
from api.dto.requests.pagination import Pagination
from api.dto.responses.event import EventResponse
from api.dto.responses.page import Page
from api.rest.repos.event import EventRepo

router = APIRouter(prefix="/events", tags=["events"])


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


@router.get("/")
def get(
    pagination: Pagination = Depends(Pagination.as_query),
    q: str | None = Query(default=None),
    location: str | None = Query(default=None),
    starts_after: datetime | None = Query(default=None),
    starts_before: datetime | None = Query(default=None),
) -> Page[EventResponse]:
    return EventRepo.get(
        pagination,
        EventListFilters(
            q=_blank_to_none(q),
            location=_blank_to_none(location),
            starts_after=starts_after,
            starts_before=starts_before,
        ),
    )

@router.get("/{event_id}")
def get_by_id(event_id: int):
    return EventRepo.get_by_id(event_id)

@router.post("/")
def create(event: CreateEvent):
    return EventRepo.create(event)

@router.patch("/{event_id}")
def update(event_id: int, event: UpdateEvent):
    return EventRepo.update_by_id(event_id, event)

@router.delete("/{event_id}")
def delete(event_id: int):
    return EventRepo.delete_by_id(event_id)
