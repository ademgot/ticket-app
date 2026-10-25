import time
from string import ascii_uppercase
from typing import LiteralString

from psycopg.sql import Composed

from api.core.sql_db import get_con
from datetime import date, timedelta, datetime
from decimal import Decimal
from faker import Faker
from random import randrange
from psycopg import sql


fake = Faker()


def hydrate_users(num: int = 100_000) -> bool:
    table_name = "users"
    cols = ["name", "email"]
    users = [(fake.name(), fake.unique.email()) for _ in range(num)]
    return _timed_insert("users", lambda: _copy_table(table_name, cols, users))


def hydrate_venues(num: int = 1_000) -> bool:
    table_name = "venues"
    cols = ["name", "timezone", "address", "state"]
    venues = [
        (f"{fake.company()} Arena {i}", fake.timezone(), fake.address(), fake.state())
        for i in range(num)
    ]
    return _timed_insert("venues", lambda: _copy_table(table_name, cols, venues))


def hydrate_tax_rates() -> bool:

    def get_states():
        with get_con() as con:
            with con.cursor() as cursor:
                cursor.execute("""
                               SELECT DISTINCT state
                               FROM venues
                               """)
                return [row["state"] for row in cursor.fetchall()]

    def generate_tax_rate(state):
        return (
            state,
            "SALES_TAX",
            Decimal(randrange(0, 1001)) / Decimal(10000),
            date(2019, 1, 1),
            date(2026, 1, 1),
        )

    table_name = "tax_rates"
    cols = [
        "jurisdiction",
        "tax_type",
        "rate",
        "effective_from",
        "effective_to"
    ]
    states = get_states()
    tax_rates = [generate_tax_rate(state) for state in states]
    return _timed_insert("tax_rates", lambda: _copy_table(table_name, cols, tax_rates))


def hydrate_events(num: int = 10_000) -> bool:
    venue_ids = _get_table_ids("venues")
    if not venue_ids:
        print("Cannot hydrate events: no venue IDs available.")
        return False

    event_durations = {
        "Comedy Night": (60, 120),
        "Jazz Concert": (90, 180),
        "Music Festival": (240, 720),
    }
    event_types = tuple(event_durations)

    def generate_event(index: int):
        event_type = fake.random_element(elements=event_types)
        min_minutes, max_minutes = event_durations[event_type]

        starts_at = datetime(2020, 1, 1) + timedelta(
            days=randrange(1827),
            hours=randrange(24),
            minutes=randrange(60),
        )
        ends_at = starts_at + timedelta(
            minutes=randrange(min_minutes, max_minutes + 1)
        )

        title = (
            fake.sentence(nb_words=2, variable_nb_words=False)
            .rstrip(".")
            .title()
        )

        return (
            f"{title} {event_type} {index}",
            fake.random_element(elements=venue_ids),
            starts_at,
            ends_at,
        )

    cols = ["name", "venue_id", "starts_at", "ends_at"]
    events = [generate_event(i) for i in range(num)]
    return _timed_insert("events", lambda: _copy_table("events", cols, events))


def hydrate_seats(rows_num: int = 20, sections=None, standing_sections=None) -> bool:
    # Build query functions
    def row_label(number: int) -> str:
        label = ""
        while number > 0:
            number, remainder = divmod(number - 1, 26)
            label = ascii_uppercase[remainder] + label
        return label

    def build_query(number_of_rows: int, secs: dict) -> Composed:
        section_values = sql.SQL(", ").join(
            sql.SQL("({}, {})").format(sql.Literal(label), sql.Literal(count))
            for label, count in secs.items()
        )

        row_values = sql.SQL(", ").join(
            sql.SQL("({})").format(sql.Literal(row_label(num)))
            for num in range(1, number_of_rows + 1)
        )
        standing_section_values = sql.SQL(", ").join(
            sql.SQL("({}, {})").format(sql.Literal(label), sql.Literal(count))
            for label, count in standing_sections.items()
        )
        return sql.SQL("""
                       INSERT INTO seats (section, seat_row, seat_number, venue_id)
                       SELECT section.label  AS section,
                              seat_row.label AS seat_row,
                              seat.num       AS seat_number,
                              venues.id      AS venue_id
                       FROM (values {sections}) AS section(label, seat_num)
                                CROSS JOIN venues
                                CROSS JOIN (values {row_values}) AS seat_row(label)
                                CROSS JOIN generate_series(1, section.seat_num) AS seat(num)
                       UNION ALL
                       SELECT section.label  AS section,
                              seat_row.label AS seat_row,
                              seat.num       AS seat_number,
                              venues.id      AS venue_id
                       FROM (values {standing_sections}) AS section(label, seat_num)
                                CROSS JOIN venues
                                CROSS JOIN (values ('special')) AS seat_row(label)
                                CROSS JOIN generate_series(1, section.seat_num) AS seat(num);
                       """).format(
            sections=section_values,
            row_values=row_values,
            standing_sections=standing_section_values
        )

    # Generate query
    if standing_sections is None:
        standing_sections = {
            "general": 1_000,
            "vip": 200,
        }
    if sections is None:
        sections = {
            "front": 50,
            "rear": 50,
            "left": 50,
            "right": 50,
        }
    query = build_query(rows_num, sections)
    return _timed_insert("seats", lambda: _execute_query(query))


def hydrate_ticket_types() -> bool:
    return _timed_insert(
        "ticket_types",
        lambda: _execute_query("""
                         INSERT INTO ticket_types(tier, event_id)
                         SELECT t_type.label, id
                         from events
                                  CROSS JOIN (VALUES ('vip'), ('general')) AS t_type(label); \
                         """),
    )


def hydrate_tickets() -> bool:
    query = """
            INSERT INTO tickets(price, seat_id, event_id, ticket_type_id)
            SELECT 
                CASE
                    WHEN seats.section = 'vip' THEN 15000
                    WHEN seats.section = 'front' OR seats.section = 'general' THEN 10000
                    WHEN seats.section = 'left' OR seats.section = 'right' THEN 7500
                    ELSE 5000
                END                AS price,
                   seats.id        AS seat_id,
                   events.id       AS event_id,
                   ticket_types.id AS ticket_type_id
            FROM events
                    INNER JOIN seats ON seats.venue_id = events.venue_id
                    INNER JOIN ticket_types ON events.id = ticket_types.event_id
                        AND ticket_types.tier = 
                            CASE
                                WHEN seats.section = 'vip' THEN 'vip'
                                ELSE 'general'
                            END;
    """
    return _timed_insert("tickets", lambda: _execute_query(query))


def hydrate_orders() -> None:
    steps = [
        (
            "Configure memory",
            "SET LOCAL work_mem = '128MB';",
        ),
        (
            "Create temporary tables",
            """
            CREATE TEMPORARY TABLE ticket_order_temp
            (
                ticket_id        integer,
                event_id         integer,
                order_id         integer,
                user_id          integer,
                price            integer,
                tax_rate         numeric(7, 4),
                tax_jurisdiction text,
                created_at       timestamptz
            );

            CREATE TEMPORARY TABLE user_lookup AS
            SELECT row_number() OVER (ORDER BY id) AS position,
                   id                              AS user_id
            FROM users;

            CREATE UNIQUE INDEX ON user_lookup (position);
            """,
        ),
        (
            "Analyze user lookup",
            "ANALYZE user_lookup;",
        ),
        (
            "Populate temporary tickets",
            """
            INSERT INTO ticket_order_temp (ticket_id, event_id, order_id, user_id,
                                           price, tax_rate, tax_jurisdiction, created_at)
            WITH selected_tickets AS (SELECT t.id        AS ticket_id,
                                             t.price,
                                             t.event_id,
                                             e.starts_at AS event_starts_at
                                      FROM tickets t
                                               JOIN events e ON e.id = t.event_id
                                      WHERE t.sold_at IS NULL
                                        AND t.held_until IS NULL
                                        AND random() < 0.85),
                 numbered_tickets AS (SELECT ticket_id,
                                             price,
                                             event_id,
                                             event_starts_at,
                                             row_number() OVER (
                                                 PARTITION BY event_id
                                                 ORDER BY ticket_id
                                                 ) AS ticket_number
                                      FROM selected_tickets),
                 ticket_count AS (SELECT event_id,
                                         event_starts_at,
                                         count(*) AS total_tickets
                                  FROM numbered_tickets
                                  GROUP BY event_id, event_starts_at),
                 orders_generated AS (SELECT tc.event_id,
                                             generated.order_number,
                                             floor(random() * 5)::integer + 1    AS size,
                                             tc.event_starts_at
                                                 - random() * INTERVAL '90 days' AS created_at
                                      FROM ticket_count tc
                                               CROSS JOIN LATERAL generate_series(
                                              1, tc.total_tickets
                                                                  ) AS generated(order_number)),
                 order_ranges AS (SELECT event_id,
                                         order_number,
                                         size,
                                         sum(size) OVER (
                                             PARTITION BY event_id
                                             ORDER BY order_number
                                             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                                             ) - size + 1 AS start_inclusive,
                                         sum(size) OVER (
                                             PARTITION BY event_id
                                             ORDER BY order_number
                                             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                                             )            AS end_inclusive,
                                         created_at
                                  FROM orders_generated),
                 user_pool AS (SELECT count(*) AS size
                               FROM user_lookup),
                 generated_orders AS (SELECT r.event_id,
                                             r.start_inclusive,
                                             least(r.end_inclusive, tc.total_tickets)
                                                   AS end_inclusive,
                                             row_number() OVER (
                                                 ORDER BY r.event_id, r.order_number
                                                 ) AS order_id,
                                             floor(random() * pool.size)::bigint + 1
                                                   AS user_position,
                                             r.created_at
                                      FROM order_ranges r
                                               JOIN ticket_count tc ON tc.event_id = r.event_id
                                               CROSS JOIN user_pool pool
                                      WHERE r.start_inclusive <= tc.total_tickets),
                 order_ticket_mapping AS (SELECT o.event_id,
                                                 o.order_id,
                                                 o.user_position,
                                                 o.created_at,
                                                 numbers.ticket_number
                                          FROM generated_orders o
                                                   CROSS JOIN LATERAL generate_series(
                                                  o.start_inclusive, o.end_inclusive
                                                                      ) AS numbers(ticket_number))
            SELECT nt.ticket_id,
                   nt.event_id,
                   mapping.order_id,
                   ul.user_id,
                   nt.price,
                   tr.rate,
                   tr.jurisdiction,
                   mapping.created_at
            FROM numbered_tickets nt
                     JOIN order_ticket_mapping mapping
                          ON mapping.event_id = nt.event_id
                              AND mapping.ticket_number = nt.ticket_number
                     JOIN user_lookup ul
                          ON ul.position = mapping.user_position
                     JOIN events e ON e.id = nt.event_id
                     JOIN venues v ON v.id = e.venue_id
                     JOIN tax_rates tr ON tr.jurisdiction = v.state;
            """,
        ),
        (
            "Analyze temporary tickets",
            "ANALYZE ticket_order_temp;",
        ),
        (
            "Insert orders",
            """
            INSERT INTO orders (id, status, user_id, subtotal, tax_amount,
                                total_charged, tax_rate_applied, tax_jurisdiction,
                                created_at, updated_at)
            WITH order_group AS (SELECT order_id,
                                        user_id,
                                        tax_rate,
                                        tax_jurisdiction,
                                        sum(price) AS subtotal,
                                        created_at
                                 FROM ticket_order_temp
                                 GROUP BY order_id, user_id, tax_rate,
                                          tax_jurisdiction, created_at)
            SELECT order_id,
                   'paid',
                   user_id,
                   subtotal,
                   round(subtotal * tax_rate),
                   subtotal + round(subtotal * tax_rate),
                   tax_rate,
                   tax_jurisdiction,
                   created_at,
                   created_at
            FROM order_group;
            """,
        ),
        (
            "Insert order items",
            """
            INSERT INTO order_items (order_id, ticket_id, created_at, updated_at)
            SELECT order_id, ticket_id, created_at, created_at
            FROM ticket_order_temp;
            """,
        ),
        (
            "Update tickets",
            """
            UPDATE tickets AS t
            SET sold_at    = tmp.created_at,
                held_until = NULL,
                updated_at = tmp.created_at
            FROM ticket_order_temp AS tmp
            WHERE t.id = tmp.ticket_id;
            """,
        ),
    ]

    total_started = time.perf_counter()

    with get_con() as con:
        with con.cursor() as cursor:
            # Report this PID so you can inspect activity from another console.
            cursor.execute("SELECT pg_backend_pid() AS pid")
            pid = cursor.fetchone()["pid"]
            print(f"Order hydration backend PID: {pid}", flush=True)

            for label, statement in steps:
                print(f"Starting: {label}", flush=True)
                started = time.perf_counter()

                cursor.execute(statement)

                print(
                    f"Finished: {label} in "
                    f"{time.perf_counter() - started:.2f}s",
                    flush=True,
                )

        print("Starting: commit", flush=True)
        started = time.perf_counter()
        con.commit()
        print(
            f"Finished: commit in {time.perf_counter() - started:.2f}s",
            flush=True,
        )

    print(
        f"Order hydration complete in "
        f"{time.perf_counter() - total_started:.2f}s",
        flush=True,
    )


def _copy_table(table_name: str, cols: list[str], data: list) -> bool:
    with get_con() as con:
        cursor = con.cursor()
        copy_query = sql.SQL("COPY {}({}) FROM STDIN").format(
            sql.Identifier(table_name),
            sql.SQL(", ").join(sql.Identifier(col) for col in cols),
        )
        with cursor.copy(copy_query) as copy:
            for row in data:
                copy.write_row(row)
        con.commit()
        return True


def _execute_query(query: Composed | LiteralString) -> bool:
    with get_con() as con:
        cursor = con.cursor()
        cursor.execute(query)
        con.commit()
        return True


def _get_table_ids(table_name: str) -> list[int]:
    with get_con() as con:
        cursor = con.cursor()
        query = sql.SQL("SELECT id FROM {table_name}").format(table_name=sql.Identifier(table_name))
        cursor.execute(query)
        return [row["id"] for row in cursor.fetchall()]


def _timed_insert(label: str, action) -> bool:
    start_time = time.perf_counter()
    resp = action()
    end_time = time.perf_counter()
    print(f"Inserted {label} in {end_time - start_time} seconds")
    return resp


def main():
    try:
        start_time = time.perf_counter()
        hydrate_users(num=100_000)
        hydrate_venues(num=1_000)
        hydrate_tax_rates()
        hydrate_events(num=10_000)
        hydrate_seats(10)
        hydrate_ticket_types()
        hydrate_tickets()
        hydrate_orders()
        end_time = time.perf_counter()
        print(f"Hydration complete in {end_time - start_time} seconds")
    except Exception as e:
        print(f"Hydration failed: {e}")
        _reset_tables()
        raise

def _reset_tables() -> None:
    _execute_query(
        """
        TRUNCATE TABLE
            order_items, orders, tickets, ticket_types,
            seats, events, tax_rates, venues, users
            RESTART IDENTITY;
        """
    )
    print("Tables are reset")

if __name__ == "__main__":
    _reset_tables()
    main()