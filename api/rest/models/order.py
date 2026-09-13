from typing import Optional
from pydantic import BaseModel, Field

class Order(BaseModel):
    id: Optional[int] = Field()
    status: str = Field()
    user_id: int = Field()
    total_price: int = Field()
    created_at: int = Field()
    updated_at: int = Field()
