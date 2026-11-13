from datetime import datetime

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: int = Field()
    email: str = Field()
    name: str = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()
