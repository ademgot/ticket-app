from typing import Optional
from pydantic import BaseModel, Field

class CreateOrder(BaseModel):
    status: str = Field()
    user_id: int = Field()
    subtotal: int = Field(ge=0)
    tax_amount: int = Field(ge=0)
    total_charged: int = Field(ge=0)
    tax_rate_applied: float = Field(ge=0)
    tax_jurisdiction: str = Field(min_length=1)

class UpdateOrder(BaseModel):
    status: Optional[str] = Field(default=None)
    user_id: Optional[int] = Field(default=None)
    subtotal: Optional[int] = Field(default=None, ge=0)
    tax_amount: Optional[int] = Field(default=None, ge=0)
    total_charged: Optional[int] = Field(default=None, ge=0)
    tax_rate_applied: Optional[float] = Field(default=None, ge=0)
    tax_jurisdiction: Optional[str] = Field(default=None, min_length=1)
