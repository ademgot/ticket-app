from datetime import datetime

from pydantic import BaseModel, Field


class VenueResponse(BaseModel):
    id: int = Field()
    name: str = Field()
    timezone: str = Field()
    address: str = Field()
    state: str = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()
