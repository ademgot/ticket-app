from typing import Optional
from pydantic import BaseModel, Field

class CreateVenue(BaseModel):
    name: str = Field(min_length=1)
    timezone: str = Field(min_length=1)
    address: str = Field(min_length=1)

class UpdateVenue(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    timezone: Optional[str] = Field(default=None, min_length=1)
    address: Optional[str] = Field(default=None, min_length=1)
