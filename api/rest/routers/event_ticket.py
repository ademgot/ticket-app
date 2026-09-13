from fastapi import APIRouter
from api.dto.requests.event_ticket import CreateEventTicket, UpdateEventTicket
from api.rest.repos.event_ticket import EventTicketRepo

router = APIRouter(prefix="/event-tickets", tags=["event-tickets"])

@router.get("/")
def get():
    return EventTicketRepo.get()

@router.get("/{event_ticket_id}")
def get_by_id(event_ticket_id: int):
    return EventTicketRepo.get_by_id(event_ticket_id)

@router.post("/")
def create(event_ticket: CreateEventTicket):
    return EventTicketRepo.create(event_ticket)

@router.patch("/{event_ticket_id}")
def update(event_ticket_id: int, event_ticket: UpdateEventTicket):
    return EventTicketRepo.update_by_id(event_ticket_id, event_ticket)

@router.delete("/{event_ticket_id}")
def delete(event_ticket_id: int):
    return EventTicketRepo.delete_by_id(event_ticket_id)
