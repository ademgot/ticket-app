from fastapi import APIRouter

from api.dto.requests.ticket_type import CreateTicketType, UpdateTicketType
from api.rest.repos.ticket_type import TicketTypeRepo


router = APIRouter(prefix="/ticket-types", tags=["ticket-types"])


@router.get("/")
def get():
    return TicketTypeRepo.get()


@router.get("/{ticket_type_id}")
def get_by_id(ticket_type_id: int):
    return TicketTypeRepo.get_by_id(ticket_type_id)


@router.post("/")
def create(ticket_type: CreateTicketType):
    return TicketTypeRepo.create(ticket_type)


@router.patch("/{ticket_type_id}")
def update(ticket_type_id: int, ticket_type: UpdateTicketType):
    return TicketTypeRepo.update_by_id(ticket_type_id, ticket_type)


@router.delete("/{ticket_type_id}")
def delete(ticket_type_id: int):
    return TicketTypeRepo.delete_by_id(ticket_type_id)
