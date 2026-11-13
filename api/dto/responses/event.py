from datetime import datetime

from pydantic import BaseModel, Field


class EventResponse(BaseModel):
    id: int = Field()
    name: str = Field()
    venue_id: int = Field()
    starts_at: datetime = Field()
    ends_at: datetime = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()
    venue_name: str | None = Field(default=None)
