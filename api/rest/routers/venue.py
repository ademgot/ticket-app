from fastapi import APIRouter
from api.dto.requests.venue import CreateVenue, UpdateVenue
from api.rest.repos.venue import VenueRepo

router = APIRouter(prefix="/venues", tags=["venues"])

@router.get("/")
def get():
    return VenueRepo.get()

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
