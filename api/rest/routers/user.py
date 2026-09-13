from fastapi import APIRouter

from api.dto.requests.user import CreateUser, UpdateUser
from api.rest.repos.user import UserRepo


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
def get():
    return UserRepo.get()

@router.get("/{user_id}")
def get_by_id(user_id: int):
    return UserRepo.get_by_id(user_id)

@router.post("/")
def create(user: CreateUser):
    return UserRepo.create(user)

@router.patch("/{user_id}")
def update(user_id: int, user: UpdateUser):
    return UserRepo.update_by_id(user_id, user)

@router.delete("/{user_id}")
def delete(user_id: int):
    return UserRepo.delete_by_id(user_id)