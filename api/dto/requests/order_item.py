from typing import Optional
from pydantic import BaseModel, Field

class CreateOrderItem(BaseModel):
    quantity: int = Field()
    order_id: int = Field()
    event_ticket_id: int = Field()
    price_paid: int = Field()

class UpdateOrderItem(BaseModel):
    quantity: Optional[int] = Field()
    order_id: Optional[int] = Field()
    event_ticket_id: Optional[int] = Field()
    price_paid: Optional[int] = Field()
