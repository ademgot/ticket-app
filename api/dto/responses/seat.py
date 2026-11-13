from datetime import datetime

from pydantic import BaseModel, Field


class SeatResponse(BaseModel):
    id: int = Field()
    section: str = Field()
    seat_row: str = Field()
    seat_number: str = Field()
    venue_id: int = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()
