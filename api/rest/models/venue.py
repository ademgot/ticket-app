from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class Venue(BaseModel):
    id: Optional[int] = Field(default=None)
    name: str = Field()
    timezone: str = Field()
    address: str = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()
