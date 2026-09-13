from typing import Optional
from pydantic import BaseModel, Field

class CreateEvent(BaseModel):
    name: str = Field()
    venue_id: int = Field()
    starts_at: int = Field()
    ends_at: int = Field()

class UpdateEvent(BaseModel):
    name: Optional[str] = Field()
    venue_id: Optional[int] = Field()
    starts_at: Optional[int] = Field()
    ends_at: Optional[int] = Field()
