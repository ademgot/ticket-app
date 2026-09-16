from typing import Optional
from pydantic import BaseModel, Field

class CreateTicket(BaseModel):
    price: int = Field(ge=0)
    held_until: Optional[int] = Field(default=None)
    sold_at: Optional[int] = Field(default=None)
    seat_id: int = Field()
    ticket_type_id: int = Field()

class UpdateTicket(BaseModel):
    price: Optional[int] = Field(default=None, ge=0)
    held_until: Optional[int] = Field(default=None)
    sold_at: Optional[int] = Field(default=None)
    seat_id: Optional[int] = Field(default=None)
    ticket_type_id: Optional[int] = Field(default=None)
