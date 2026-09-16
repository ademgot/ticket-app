from fastapi import APIRouter

from api.dto.requests.seat import CreateSeat, UpdateSeat
from api.rest.repos.seat import SeatRepo


router = APIRouter(prefix="/seats", tags=["seats"])


@router.get("/")
def get():
    return SeatRepo.get()


@router.get("/{seat_id}")
def get_by_id(seat_id: int):
    return SeatRepo.get_by_id(seat_id)


@router.post("/")
def create(seat: CreateSeat):
    return SeatRepo.create(seat)


@router.patch("/{seat_id}")
def update(seat_id: int, seat: UpdateSeat):
    return SeatRepo.update_by_id(seat_id, seat)


@router.delete("/{seat_id}")
def delete(seat_id: int):
    return SeatRepo.delete_by_id(seat_id)
