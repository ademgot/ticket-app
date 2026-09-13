from typing import Optional
from pydantic import BaseModel, Field

class Ticket(BaseModel):
    id: Optional[int] = Field()
    tier: str = Field()
    created_at: int = Field()
    updated_at: int = Field()
