from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class Ticket(BaseModel):
    id: Optional[int] = Field(default=None)
    price: int = Field()
    held_until: Optional[datetime] = Field(default=None)
    sold_at: Optional[datetime] = Field(default=None)
    held_by_user_id: Optional[int] = Field(default=None)
    sold_to_user_id: Optional[int] = Field(default=None)
    seat_id: int = Field()
    event_id: int = Field()
    ticket_type_id: int = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()
