from typing import Optional

from pydantic import BaseModel, Field


class TicketType(BaseModel):
    id: Optional[int] = Field(default=None)
    tier: str = Field()
    event_id: int = Field()
    created_at: int = Field()
    updated_at: int = Field()
