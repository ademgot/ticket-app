from typing import Optional
from pydantic import BaseModel, Field

class CreateVenue(BaseModel):
    capacity: int = Field()

class UpdateVenue(BaseModel):
    capacity: Optional[int] = Field()
