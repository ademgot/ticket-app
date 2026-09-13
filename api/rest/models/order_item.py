from typing import Optional
from pydantic import BaseModel, Field

class OrderItem(BaseModel):
    id: Optional[int] = Field()
    quantity: int = Field()
    order_id: int = Field()
    event_ticket_id: int = Field()
    price_paid: int = Field()
    created_at: int = Field()
    updated_at: int = Field()
