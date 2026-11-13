from datetime import datetime

from pydantic import BaseModel, Field


class TicketTypeResponse(BaseModel):
    id: int = Field()
    tier: str = Field()
    event_id: int = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()
