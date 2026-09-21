from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class CreateTicket(BaseModel):
    price: int = Field(ge=0)
    seat_id: int = Field()
    event_id: int = Field()
    ticket_type_id: int = Field()

class UpdateTicket(BaseModel):
    price: Optional[int] = Field(default=None, ge=0)
    held_until: Optional[datetime] = Field(default=None)
    sold_at: Optional[datetime] = Field(default=None)
    held_by_user_id: Optional[int] = Field(default=None)
    sold_to_user_id: Optional[int] = Field(default=None)
    seat_id: Optional[int] = Field(default=None)
    event_id: Optional[int] = Field(default=None)
    ticket_type_id: Optional[int] = Field(default=None)
