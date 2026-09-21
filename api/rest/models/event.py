from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class Event(BaseModel):
    id: Optional[int] = Field(default=None)
    name: str = Field()
    venue_id: int = Field()
    starts_at: datetime = Field()
    ends_at: datetime = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()
