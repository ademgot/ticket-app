from fastapi import APIRouter
from api.dto.requests.event import CreateEvent, UpdateEvent
from api.rest.repos.event import EventRepo

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/")
def get():
    return EventRepo.get()

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
