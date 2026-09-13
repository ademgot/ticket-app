from typing import Optional
from pydantic import BaseModel, Field

class Venue(BaseModel):
    id: Optional[int] = Field()
    capacity: int = Field()
    created_at: int = Field()
    updated_at: int = Field()
