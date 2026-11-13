from fastapi import APIRouter, Depends
from api.dto.requests.order_item import CreateOrderItem
from api.dto.requests.pagination import Pagination
from api.dto.responses.order_item import OrderItemResponse
from api.dto.responses.page import Page
from api.rest.repos.order_item import OrderItemRepo

router = APIRouter(prefix="/order-items", tags=["order-items"])

@router.get("/")
def get(pagination: Pagination = Depends(Pagination.as_query)) -> Page[OrderItemResponse]:
    return OrderItemRepo.get(pagination)

@router.get("/{order_id}/{ticket_id}")
def get_by_id(order_id: int, ticket_id: int):
    return OrderItemRepo.get_by_id(order_id, ticket_id)

@router.post("/")
def create(order_item: CreateOrderItem):
    return OrderItemRepo.create(order_item)

@router.delete("/{order_id}/{ticket_id}")
def delete(order_id: int, ticket_id: int):
    return OrderItemRepo.delete_by_id(order_id, ticket_id)
