from fastapi import APIRouter, Depends
from api.dto.requests.pagination import Pagination
from api.dto.requests.venue import CreateVenue, UpdateVenue
from api.dto.responses.page import Page
from api.dto.responses.venue import VenueResponse
from api.rest.repos.venue import VenueRepo

router = APIRouter(prefix="/venues", tags=["venues"])

@router.get("/")
def get(pagination: Pagination = Depends(Pagination.as_query)) -> Page[VenueResponse]:
    return VenueRepo.get(pagination)

@router.get("/{venue_id}")
def get_by_id(venue_id: int):
    return VenueRepo.get_by_id(venue_id)

@router.post("/")
def create(venue: CreateVenue):
    return VenueRepo.create(venue)

@router.patch("/{venue_id}")
def update(venue_id: int, venue: UpdateVenue):
    return VenueRepo.update_by_id(venue_id, venue)

@router.delete("/{venue_id}")
def delete(venue_id: int):
    return VenueRepo.delete_by_id(venue_id)
