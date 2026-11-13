from fastapi import APIRouter, Depends
from api.dto.requests.order import CreateOrder, UpdateOrder
from api.dto.requests.pagination import Pagination
from api.dto.responses.order import OrderResponse
from api.dto.responses.page import Page
from api.rest.repos.order import OrderRepo

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/")
def get(pagination: Pagination = Depends(Pagination.as_query)) -> Page[OrderResponse]:
    return OrderRepo.get(pagination)

@router.get("/{order_id}")
def get_by_id(order_id: int):
    return OrderRepo.get_by_id(order_id)

@router.post("/")
def create(order: CreateOrder):
    return OrderRepo.create(order)

@router.patch("/{order_id}")
def update(order_id: int, order: UpdateOrder):
    return OrderRepo.update_by_id(order_id, order)

@router.delete("/{order_id}")
def delete(order_id: int):
    return OrderRepo.delete_by_id(order_id)
