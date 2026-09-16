from typing import Optional

from pydantic import BaseModel, Field


class CreateSeat(BaseModel):
    section: str = Field(min_length=1)
    seat_row: str = Field(min_length=1)
    seat_number: str = Field(min_length=1)
    venue_id: int = Field()


class UpdateSeat(BaseModel):
    section: Optional[str] = Field(default=None, min_length=1)
    seat_row: Optional[str] = Field(default=None, min_length=1)
    seat_number: Optional[str] = Field(default=None, min_length=1)
    venue_id: Optional[int] = Field(default=None)
