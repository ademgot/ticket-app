from readline import insert_text
from string import ascii_uppercase
from typing import LiteralString

from psycopg.sql import Composed

from api.core.sql_db import get_con
from datetime import date, timedelta, datetime
from decimal import Decimal
from faker import Faker
from random import randrange
from psycopg import DatabaseError, sql


fake = Faker()


def hydrate_users(num: int = 100000) -> bool:
    table_name = "users"
    cols = ["name", "email"]
    users = [(fake.name(), fake.email()) for _ in range(num)]
    return _copy_table(table_name, cols, users)


def hydrate_venues(num: int = 1000) -> bool:
    table_name = "venues"
    cols = ["name", "timezone", "address"]
    venues = [(fake.building_name(), fake.timezone(), fake.address()) for _ in range(num)]
    return _copy_table(table_name, cols, venues)


def hydrate_tax_rates(num: int = 50) -> bool:
    def generate_tax_rate():
        effective_from = date(2020, 1, 1) + timedelta(days=randrange(1827))
        effective_to = effective_from + timedelta(days=randrange(30, 366))
        return (
            fake.state(),
            "SALES_TAX",
            Decimal(randrange(0, 1001)) / Decimal(10000),
            effective_from,
            effective_to,
        )

    table_name = "tax_rates"
    cols = [
        "jurisdiction",
        "tax_type",
        "rate",
        "effective_from",
        "effective_to"
    ]
    tax_rates = [generate_tax_rate() for _ in range(num)]
    return _copy_table(table_name, cols, tax_rates)


def hydrate_event(num: int = 10000) -> bool:
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

    def generate_event():
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
            f"{title} {event_type}",
            fake.random_element(elements=venue_ids),
            starts_at,
            ends_at,
        )

    cols = ["name", "venue_id", "starts_at", "ends_at"]
    events = [generate_event() for _ in range(num)]
    return _copy_table("events", cols, events)


def hydrate_seats(rows_num: int = 50, sections=None, standing_sections=None) -> bool:
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
            "general": 5000,
            "vip": 1000,
        }
    if sections is None:
        sections = {
            "front": 100,
            "rear": 100,
            "left": 100,
            "right": 100,
        }
    query = build_query(rows_num, sections)
    return _insert_table(query)


def hydrate_ticket_types() -> bool:
    return _insert_table("""
                         INSERT INTO ticket_types(tier, event_id)
                         SELECT t_type.label, id
                         from events
                                  CROSS JOIN (VALUES ('vip'), ('general')) AS t_type(label); \
                         """)


def hydrate_tickets() -> bool:
    query = """
            INSERT INTO tickets(price, seat_id, event_id, ticket_type_id)
            SELECT 
                CASE
                    WHEN seats.section = 'vip' THEN 150
                    WHEN seats.section = 'front' OR seats.section = 'general' THEN 100
                    WHEN seats.section = 'left' OR seats.section = 'right' THEN 75
                    ELSE 50
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
    return _insert_table(query)


def hydrate_order_items(num: int = 1000000) -> bool:
    pass


def hydrate_orders(num: int = 1000000) -> bool:
    pass


def _copy_table(table_name: str, cols: list[str], data: list) -> bool:
    try:
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
    except DatabaseError as e:
        print(e)
        return False


def _insert_table(query:Composed|LiteralString) -> bool:
    try:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute(query)
            con.commit()
            return True
    except DatabaseError as e:
        print(e)
        return False


def _get_table_ids(table_name: str) -> list[int]:
    try:
        with get_con() as con:
            cursor = con.cursor()
            query = sql.SQL("SELECT id FROM {table_name}").format(table_name=sql.Identifier(table_name))
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]
    except DatabaseError as e:
        print(e)
        return []


def main():
    pass

if __name__ == "__main__":
    main()