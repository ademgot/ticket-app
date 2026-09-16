from typing import Optional

from pydantic import BaseModel, Field


class TaxRate(BaseModel):
    id: Optional[int] = Field(default=None)
    jurisdiction: str = Field()
    tax_type: str = Field()
    rate: float = Field()
    effective_from: int = Field()
    effective_to: Optional[int] = Field(default=None)
    created_at: int = Field()
    updated_at: int = Field()
