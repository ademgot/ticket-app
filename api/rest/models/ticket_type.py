from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TicketType(BaseModel):
    id: Optional[int] = Field(default=None)
    tier: str = Field()
    event_id: int = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()
