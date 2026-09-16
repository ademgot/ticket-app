from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, field_validator


class CreateVenue(BaseModel):
    name: str = Field(min_length=1)
    timezone: str = Field(min_length=1)
    address: str = Field(min_length=1)

class UpdateVenue(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    timezone: Optional[str] = Field(default=None, min_length=1)
    address: Optional[str] = Field(default=None, min_length=1)

    @field_validator("timezone")
    @classmethod
    def validate_timezones(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                ZoneInfo(v)
            except ZoneInfoNotFoundError:
                raise ValueError(f"Invalid timezone: {v}")
        return v
