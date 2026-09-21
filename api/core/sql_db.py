import psycopg
from contextlib import contextmanager
from psycopg import Connection
from psycopg.rows import dict_row
from typing import Any, Generator


@contextmanager
def get_con() -> Generator[Connection, Any, None]:
    with psycopg.connect(
        "user=postgres password=example host=localhost port=5432",
        row_factory=dict_row,
    ) as conn:
        try:
            yield conn
        except:
            conn.rollback()
            raise
        finally:
            conn.close()
