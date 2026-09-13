from typing import Optional
from pydantic import BaseModel, Field

class CreateOrder(BaseModel):
    status: str = Field()
    user_id: int = Field()
    total_price: int = Field()

class UpdateOrder(BaseModel):
    status: Optional[str] = Field()
    user_id: Optional[int] = Field()
    total_price: Optional[int] = Field()
