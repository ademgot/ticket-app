from pydantic import BaseModel
from typing import Any, List


def generate_sql_update_query_setter(model: BaseModel) -> tuple[str|None, List[Any]|None]:
    arr = model.model_dump()
    q = ""
    vals = []
    for k,v in arr:
        if v is not None:
            q += k + " = ?"
            vals.append(v)
    if q != "":
        return q, vals
    return None, None