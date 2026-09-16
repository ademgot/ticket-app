from typing import Optional

from pydantic import BaseModel, Field


class Seat(BaseModel):
    id: Optional[int] = Field(default=None)
    section: str = Field()
    seat_row: str = Field()
    seat_number: str = Field()
    venue_id: int = Field()
    created_at: int = Field()
    updated_at: int = Field()
