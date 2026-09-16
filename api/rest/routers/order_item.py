from fastapi import APIRouter
from api.dto.requests.order_item import CreateOrderItem
from api.rest.repos.order_item import OrderItemRepo

router = APIRouter(prefix="/order-items", tags=["order-items"])

@router.get("/")
def get():
    return OrderItemRepo.get()

@router.get("/{order_id}/{ticket_id}")
def get_by_id(order_id: int, ticket_id: int):
    return OrderItemRepo.get_by_id(order_id, ticket_id)

@router.post("/")
def create(order_item: CreateOrderItem):
    return OrderItemRepo.create(order_item)

@router.delete("/{order_id}/{ticket_id}")
def delete(order_id: int, ticket_id: int):
    return OrderItemRepo.delete_by_id(order_id, ticket_id)
