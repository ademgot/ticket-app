from datetime import datetime

from pydantic import BaseModel, Field


class OrderItemResponse(BaseModel):
    order_id: int = Field()
    ticket_id: int = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()
