from fastapi import Query
from pydantic import BaseModel, Field


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @classmethod
    def as_query(
        cls,
        page: int = Query(1, ge=1),
        page_size: int = Query(50, ge=1, le=100),
    ) -> "Pagination":
        return cls(page=page, page_size=page_size)
