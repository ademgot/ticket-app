from typing import Optional
from pydantic import BaseModel, Field

class Order(BaseModel):
    id: Optional[int] = Field(default=None)
    status: str = Field()
    user_id: int = Field()
    subtotal: int = Field()
    tax_amount: int = Field()
    total_charged: int = Field()
    tax_rate_applied: float = Field()
    tax_jurisdiction: str = Field()
    created_at: int = Field()
    updated_at: int = Field()
