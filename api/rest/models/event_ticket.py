from typing import Optional
from pydantic import BaseModel, Field

class EventTicket(BaseModel):
    id: Optional[int] = Field()
    quantity_available: int = Field()
    price: int = Field()
    event_id: int = Field()
    ticket_id: int = Field()
    created_at: int = Field()
    updated_at: int = Field()
