from typing import Optional
from pydantic import BaseModel, Field

class Venue(BaseModel):
    id: Optional[int] = Field(default=None)
    name: str = Field()
    timezone: str = Field()
    address: str = Field()
    created_at: int = Field()
    updated_at: int = Field()
