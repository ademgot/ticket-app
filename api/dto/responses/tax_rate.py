from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TaxRateResponse(BaseModel):
    id: int = Field()
    jurisdiction: str = Field()
    tax_type: str = Field()
    rate: float = Field()
    effective_from: datetime = Field()
    effective_to: Optional[datetime] = Field(default=None)
    created_at: datetime = Field()
    updated_at: datetime = Field()
