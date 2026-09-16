from typing import Optional

from pydantic import BaseModel, Field


class CreateTaxRate(BaseModel):
    jurisdiction: str = Field(min_length=1)
    tax_type: str = Field(min_length=1)
    rate: float = Field(ge=0)
    effective_from: int = Field()
    effective_to: Optional[int] = Field(default=None)


class UpdateTaxRate(BaseModel):
    jurisdiction: Optional[str] = Field(default=None, min_length=1)
    tax_type: Optional[str] = Field(default=None, min_length=1)
    rate: Optional[float] = Field(default=None, ge=0)
    effective_from: Optional[int] = Field(default=None)
    effective_to: Optional[int] = Field(default=None)
