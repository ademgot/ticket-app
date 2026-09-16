from typing import Optional
from pydantic import BaseModel, Field

class Ticket(BaseModel):
    id: Optional[int] = Field(default=None)
    price: int = Field()
    held_until: Optional[int] = Field(default=None)
    sold_at: Optional[int] = Field(default=None)
    seat_id: int = Field()
    event_id: int = Field()
    ticket_type_id: int = Field()
    created_at: int = Field()
    updated_at: int = Field()
