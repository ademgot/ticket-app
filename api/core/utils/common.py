from pydantic import BaseModel
from typing import Any
from fastapi import Request
from fastapi.responses import JSONResponse


def generate_sql_update_query_setter(
    model: BaseModel,
) -> tuple[str | None, list[Any] | None]:
    fields = model.model_dump(exclude_unset=True)
    if fields:
        assignments = [f"{name} = %s" for name in fields]
        assignments.append("updated_at = NOW()")
        return "SET " + ", ".join(assignments), list(fields.values())
    return None, None


def handle_integrity_error(_request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": f"Conflicts with existing data: {exc}"},
    )