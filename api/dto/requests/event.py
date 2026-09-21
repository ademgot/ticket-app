from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class CreateEvent(BaseModel):
    name: str = Field(min_length=1)
    venue_id: int = Field()
    starts_at: datetime = Field()
    ends_at: datetime = Field()

class UpdateEvent(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    venue_id: Optional[int] = Field(default=None)
    starts_at: Optional[datetime] = Field(default=None)
    ends_at: Optional[datetime] = Field(default=None)
