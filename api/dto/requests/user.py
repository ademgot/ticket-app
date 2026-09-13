from typing import Optional
from pydantic import BaseModel, Field


class CreateUser(BaseModel):
    name: str = Field()
    email: str = Field()


class UpdateUser(BaseModel):
    name: Optional[str] = Field()
    email: Optional[str] = Field()