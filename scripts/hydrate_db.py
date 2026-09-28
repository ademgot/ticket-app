from readline import insert_text

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
    except DatabaseError as e:
        print(e)
        return False
    return True


def _generate_series_table(table_name: str, cols: list[str]) -> bool:
    try:
        with get_con() as con:
            cursor = con.cursor()
            insert_query = """
            select
                section.label as section,
                seat_row.label as row,
                case
                    when section.label = 'general' then seat.num + seat_row.offset_num
                    else seat.num
                end as seat,
                venues.id
            from (values ('general', 5), ('vip', 2)) as section(label, seat_num)
            cross join venues
            cross join (values(0, 'A'), (5, 'B'), (10, 'C')) as seat_row(offset_num, label)
            cross join generate_series(1, section.seat_num) as seat(num)
            order by venues.id, section, row, seat;
            """
            cursor.execute(insert_query)
            check = cursor.fetchone()["id"]
            con.commit()
    except DatabaseError as e:
        print(e)
        return False
    return True if check else False


def _get_table_ids(table_name: str) -> list[int]:
    try:
        with get_con() as con:
            cursor = con.cursor()
            query = sql.SQL("SELECT id FROM {}").format(sql.Identifier(table_name))
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]
    except DatabaseError as e:
        print(e)
        return []


def main():
    pass

if __name__ == "__main__":
    main()