from typing import Optional
from pydantic import BaseModel, Field

class CreateEventTicket(BaseModel):
    quantity_available: int = Field()
    price: int = Field()
    event_id: int = Field()
    ticket_id: int = Field()

class UpdateEventTicket(BaseModel):
    quantity_available: Optional[int] = Field()
    price: Optional[int] = Field()
    event_id: Optional[int] = Field()
    ticket_id: Optional[int] = Field()
