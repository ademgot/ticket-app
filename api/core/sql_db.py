import sqlite3
import os
from contextlib import contextmanager
from sqlite3 import Connection
from typing import Any, Generator


DB_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "db", "app.db")
)


def set_db_path(path: str) -> None:
    global DB_PATH
    DB_PATH = path


def migrate() -> None:
    with get_con() as con:
        has_legacy_users = con.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table' AND name = 'user'
            """
        ).fetchone()
        con.executescript("""
            CREATE TABLE IF NOT EXISTS venues (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL UNIQUE,
                timezone    TEXT NOT NULL,
                address     TEXT NOT NULL,
                created_at  INTEGER NOT NULL DEFAULT (unixepoch('now')),
                updated_at  INTEGER NOT NULL DEFAULT (unixepoch('now'))
            );

            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                email       TEXT NOT NULL UNIQUE,
                name        TEXT NOT NULL,
                created_at  INTEGER NOT NULL DEFAULT (unixepoch('now')),
                updated_at  INTEGER NOT NULL DEFAULT (unixepoch('now'))
            );

            CREATE TABLE IF NOT EXISTS events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL UNIQUE,
                venue_id    INTEGER NOT NULL REFERENCES venues(id),
                starts_at   INTEGER NOT NULL,
                ends_at     INTEGER NOT NULL,
                created_at  INTEGER NOT NULL DEFAULT (unixepoch('now')),
                updated_at  INTEGER NOT NULL DEFAULT (unixepoch('now')),
                CHECK (end > start)
            );

            CREATE TABLE IF NOT EXISTS seats (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                section     TEXT NOT NULL,
                seat_row    TEXT NOT NULL,
                seat_number TEXT NOT NULL,
                venue_id    INTEGER NOT NULL REFERENCES venues(id),
                created_at  INTEGER NOT NULL DEFAULT (unixepoch('now')),
                updated_at  INTEGER NOT NULL DEFAULT (unixepoch('now')),
                UNIQUE (venue_id, section, seat_row, seat_number)
            );

            CREATE TABLE IF NOT EXISTS ticket_types (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                tier        TEXT NOT NULL,
                event_id    INTEGER NOT NULL REFERENCES events(id),
                created_at  INTEGER NOT NULL DEFAULT (unixepoch('now')),
                updated_at  INTEGER NOT NULL DEFAULT (unixepoch('now')),
                UNIQUE (event_id, tier)
            );

            CREATE TABLE IF NOT EXISTS tickets (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                price           INTEGER NOT NULL CHECK (price >= 0),
                held_until      INTEGER,
                sold_at         INTEGER,
                seat_id         INTEGER NOT NULL REFERENCES seats(id),
                ticket_type_id  INTEGER NOT NULL REFERENCES ticket_types(id),
                created_at      INTEGER NOT NULL DEFAULT (unixepoch('now')),
                updated_at      INTEGER NOT NULL DEFAULT (unixepoch('now')),
                UNIQUE (ticket_type_id, seat_id)
            );

            CREATE TABLE IF NOT EXISTS orders (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                status              TEXT NOT NULL,
                user_id             INTEGER NOT NULL REFERENCES users(id),
                subtotal            INTEGER NOT NULL CHECK (subtotal >= 0),
                tax_amount          INTEGER NOT NULL CHECK (tax_amount >= 0),
                total_charged       INTEGER NOT NULL CHECK (total_charged >= 0),
                tax_rate_applied    REAL NOT NULL CHECK (tax_rate_applied >= 0),
                tax_jurisdiction    TEXT NOT NULL,
                created_at          INTEGER NOT NULL DEFAULT (unixepoch('now')),
                updated_at          INTEGER NOT NULL DEFAULT (unixepoch('now'))
            );

            CREATE TABLE IF NOT EXISTS order_items (
                order_id    INTEGER NOT NULL REFERENCES orders(id),
                ticket_id   INTEGER NOT NULL UNIQUE REFERENCES tickets(id),
                created_at  INTEGER NOT NULL DEFAULT (unixepoch('now')),
                updated_at  INTEGER NOT NULL DEFAULT (unixepoch('now')),
                PRIMARY KEY (order_id, ticket_id)
            );

            CREATE TABLE IF NOT EXISTS tax_rates (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                jurisdiction    TEXT NOT NULL,
                tax_type        TEXT NOT NULL,
                rate            REAL NOT NULL CHECK (rate >= 0),
                effective_from  INTEGER NOT NULL,
                effective_to    INTEGER,
                created_at      INTEGER NOT NULL DEFAULT (unixepoch('now')),
                updated_at      INTEGER NOT NULL DEFAULT (unixepoch('now')),
                CHECK (effective_to IS NULL OR effective_to > effective_from),
                UNIQUE (jurisdiction, tax_type, effective_from)
            );

            CREATE INDEX IF NOT EXISTS idx_events_venue_id ON events(venue_id);
            CREATE INDEX IF NOT EXISTS idx_seats_venue_id ON seats(venue_id);
            CREATE INDEX IF NOT EXISTS idx_ticket_types_event_id ON ticket_types(event_id);
            CREATE INDEX IF NOT EXISTS idx_tickets_seat_id ON tickets(seat_id);
            CREATE INDEX IF NOT EXISTS idx_tickets_ticket_type_id ON tickets(ticket_type_id);
            CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
            CREATE INDEX IF NOT EXISTS idx_order_items_ticket_id ON order_items(ticket_id);
            CREATE INDEX IF NOT EXISTS idx_tax_rates_lookup
                ON tax_rates(jurisdiction, tax_type, effective_from, effective_to);
        """)
        if has_legacy_users:
            con.execute(
                """
                INSERT OR IGNORE INTO users(id, email, name, created_at, updated_at)
                SELECT id, email, name, created_at, updated_at
                FROM user
                WHERE deleted_at IS NULL
                """
            )
        con.commit()


# Needs to be updated when new tables are added
def clear_db() -> None:
    with get_con() as con:
        cursor = con.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("DELETE FROM order_items")
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM tickets")
        cursor.execute("DELETE FROM ticket_types")
        cursor.execute("DELETE FROM seats")
        cursor.execute("DELETE FROM events")
        cursor.execute("DELETE FROM tax_rates")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM venues")
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
