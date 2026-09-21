from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    id: Optional[int] = Field(default=None)
    email: str = Field()
    name: str = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()