from datetime import datetime

from pydantic import BaseModel, Field


class OrderResponse(BaseModel):
    id: int = Field()
    status: str = Field()
    user_id: int = Field()
    subtotal: int = Field()
    tax_amount: int = Field()
    total_charged: int = Field()
    tax_rate_applied: float = Field()
    tax_jurisdiction: str = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()
