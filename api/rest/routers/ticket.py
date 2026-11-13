from fastapi import APIRouter, Depends
from api.dto.requests.pagination import Pagination
from api.dto.requests.ticket import CreateTicket, UpdateTicket
from api.dto.responses.page import Page
from api.dto.responses.ticket import TicketResponse
from api.rest.repos.ticket import TicketRepo

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.get("/")
def get(pagination: Pagination = Depends(Pagination.as_query)) -> Page[TicketResponse]:
    return TicketRepo.get(pagination)

@router.get("/{ticket_id}")
def get_by_id(ticket_id: int):
    return TicketRepo.get_by_id(ticket_id)

@router.post("/")
def create(ticket: CreateTicket):
    return TicketRepo.create(ticket)

@router.patch("/{ticket_id}")
def update(ticket_id: int, ticket: UpdateTicket):
    return TicketRepo.update_by_id(ticket_id, ticket)

@router.delete("/{ticket_id}")
def delete(ticket_id: int):
    return TicketRepo.delete_by_id(ticket_id)
