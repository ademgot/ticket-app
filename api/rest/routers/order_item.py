from fastapi import APIRouter
from api.dto.requests.order_item import CreateOrderItem, UpdateOrderItem
from api.rest.repos.order_item import OrderItemRepo

router = APIRouter(prefix="/order-items", tags=["order-items"])

@router.get("/")
def get():
    return OrderItemRepo.get()

@router.get("/{order_item_id}")
def get_by_id(order_item_id: int):
    return OrderItemRepo.get_by_id(order_item_id)

@router.post("/")
def create(order_item: CreateOrderItem):
    return OrderItemRepo.create(order_item)

@router.patch("/{order_item_id}")
def update(order_item_id: int, order_item: UpdateOrderItem):
    return OrderItemRepo.update_by_id(order_item_id, order_item)

@router.delete("/{order_item_id}")
def delete(order_item_id: int):
    return OrderItemRepo.delete_by_id(order_item_id)
