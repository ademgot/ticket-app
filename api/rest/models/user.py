from typing import Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    id: Optional[int] = Field(default=None)
    email: str = Field()
    name: str = Field()
    created_at: int = Field()
    updated_at: int = Field()