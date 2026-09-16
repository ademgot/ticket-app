from pydantic import BaseModel
from typing import Any


def generate_sql_update_query_setter(
    model: BaseModel,
) -> tuple[str | None, list[Any] | None]:
    fields = model.model_dump(exclude_unset=True)
    if fields:
        assignments = [f"{name} = ?" for name in fields]
        assignments.append("updated_at = unixepoch('now')")
        return "SET " + ", ".join(assignments), list(fields.values())
    return None, None