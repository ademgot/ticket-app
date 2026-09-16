from typing import Optional
from pydantic import BaseModel, Field

class Event(BaseModel):
    id: Optional[int] = Field(default=None)
    name: str = Field()
    venue_id: int = Field()
    starts_at: int = Field()
    ends_at: int = Field()
    created_at: int = Field()
    updated_at: int = Field()
