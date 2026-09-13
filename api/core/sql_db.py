import sqlite3
import os
from contextlib import contextmanager
from sqlite3 import Connection
from typing import Any, Generator


DB_PATH = "db/app.db"


def set_db_path(path: str) -> None:
    global DB_PATH
    DB_PATH = path


def migrate() -> None:
    with get_con() as con:
        cursor = con.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS venue (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                capacity    INTEGER,
                created_at  INTEGER DEFAULT (unixepoch('now')),
                updated_at  INTEGER DEFAULT (unixepoch('now')),
                deleted_at  INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                email       TEXT UNIQUE,
                name        TEXT,
                created_at  INTEGER DEFAULT (unixepoch('now')),
                updated_at  INTEGER DEFAULT (unixepoch('now')),
                deleted_at  INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ticket (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                tier        TEXT,
                created_at  INTEGER DEFAULT (unixepoch('now')),
                updated_at  INTEGER DEFAULT (unixepoch('now')),
                deleted_at  INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT,
                venue_id    INTEGER REFERENCES venue(id),
                starts_at   INTEGER,
                ends_at     INTEGER,
                created_at  INTEGER DEFAULT (unixepoch('now')),
                updated_at  INTEGER DEFAULT (unixepoch('now')),
                deleted_at  INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_ticket (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                quantity_available  INTEGER,
                price               INTEGER,
                event_id            INTEGER REFERENCES event(id),
                ticket_id           INTEGER REFERENCES ticket(id),
                created_at          INTEGER DEFAULT (unixepoch('now')),
                updated_at          INTEGER DEFAULT (unixepoch('now')),
                deleted_at          INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "order" (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                status      TEXT,
                user_id     INTEGER REFERENCES user(id),
                total_price INTEGER,
                created_at  INTEGER DEFAULT (unixepoch('now')),
                updated_at  INTEGER DEFAULT (unixepoch('now')),
                deleted_at  INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_item (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                quantity        INTEGER,
                order_id        INTEGER REFERENCES "order"(id),
                event_ticket_id INTEGER REFERENCES event_ticket(id),
                price_paid      INTEGER,
                created_at      INTEGER DEFAULT (unixepoch('now')),
                updated_at      INTEGER DEFAULT (unixepoch('now')),
                deleted_at      INTEGER
            )
        """)
        con.commit()


# Needs to be updated when new tables are added
def clear_db() -> None:
    with get_con() as con:
        cursor = con.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("DELETE FROM order_item")
        cursor.execute('DELETE FROM "order"')
        cursor.execute("DELETE FROM event_ticket")
        cursor.execute("DELETE FROM ticket")
        cursor.execute("DELETE FROM event")
        cursor.execute("DELETE FROM user")
        cursor.execute("DELETE FROM venue")
        cursor.execute("PRAGMA foreign_keys = ON")
        con.commit()


class _MedianAggregate:
    def __init__(self) -> None:
        self.values = []

    def step(self, value) -> None:
        if value is not None:
            self.values.append(value)

    def finalize(self) -> int | float | None:
        if not self.values:
            return None

        sorted_values = sorted(self.values)
        n = len(sorted_values)

        if n % 2 == 1:
            return sorted_values[n // 2]

        return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2


@contextmanager
def get_con() -> Generator[Connection, Any, None]:
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-64000")
    conn.execute("PRAGMA mmap_size=268435456")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.create_aggregate("median", 1, _MedianAggregate)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
    except:
        conn.rollback()
        raise
    finally:
        conn.close()
