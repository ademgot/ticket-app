from typing import Optional

from pydantic import BaseModel, Field


class CreateTicketType(BaseModel):
    tier: str = Field(min_length=1)
    event_id: int = Field()


class UpdateTicketType(BaseModel):
    tier: Optional[str] = Field(default=None, min_length=1)
    event_id: Optional[int] = Field(default=None)
