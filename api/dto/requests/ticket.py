from typing import Optional
from pydantic import BaseModel, Field

class CreateTicket(BaseModel):
    tier: str = Field()

class UpdateTicket(BaseModel):
    tier: Optional[str] = Field()
