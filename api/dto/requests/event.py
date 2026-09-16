from typing import Optional
from pydantic import BaseModel, Field

class CreateEvent(BaseModel):
    name: str = Field(min_length=1)
    venue_id: int = Field()
    starts_at: int = Field()
    ends_at: int = Field()

class UpdateEvent(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    venue_id: Optional[int] = Field(default=None)
    starts_at: Optional[int] = Field(default=None)
    ends_at: Optional[int] = Field(default=None)
