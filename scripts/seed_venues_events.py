from __future__ import annotations

import time
from sqlite3 import IntegrityError

from api.core.sql_db import migrate
from api.dto.requests.event import CreateEvent
from api.dto.requests.seat import CreateSeat
from api.dto.requests.ticket import CreateTicket
from api.dto.requests.ticket_type import CreateTicketType
from api.dto.requests.venue import CreateVenue
from api.rest.repos.event import EventRepo
from api.rest.repos.seat import SeatRepo
from api.rest.repos.ticket import TicketRepo
from api.rest.repos.ticket_type import TicketTypeRepo
from api.rest.repos.venue import VenueRepo

SEATS = [
    {"section": "Orchestra", "seat_row": row, "seat_number": number, "vip": row == "A"}
    for row in ("A", "B")
    for number in ("1", "2", "3", "4")
]

TIERS = (
    ("VIP", 12500),
    ("General Admission", 4500),
)

VENUES = [
    {
        "name": "The Grand Hall",
        "timezone": "America/New_York",
        "address": "100 Broadway, New York, NY",
        "events": [
            ("Late Set at the Grand Hall", 7, 3),
            ("Sunday Matinee", 14, 2),
        ],
    },
    {
        "name": "The Fillmore",
        "timezone": "America/Los_Angeles",
        "address": "1805 Geary Blvd, San Francisco, CA",
        "events": [
            ("West Coast Double Bill", 10, 4),
        ],
    },
    {
        "name": "Royal Albert Hall",
        "timezone": "Europe/London",
        "address": "Kensington Gore, London",
        "events": [
            ("Proms Chamber Night", 21, 3),
            ("Organ Recital", 28, 2),
        ],
    },
]


def _get_or_create_venue(name: str, timezone: str, address: str):
    existing = next((venue for venue in VenueRepo.get() if venue.name == name), None)
    if existing:
        print(f"venue exists  {name}")
        return existing
    venue = VenueRepo.create(CreateVenue(name=name, timezone=timezone, address=address))
    print(f"venue created {venue.name} (id={venue.id})")
    return venue


def _get_or_create_seat(section: str, seat_row: str, seat_number: str, venue_id: int):
    existing = next(
        (
            seat
            for seat in SeatRepo.get()
            if seat.venue_id == venue_id
            and seat.section == section
            and seat.seat_row == seat_row
            and seat.seat_number == seat_number
        ),
        None,
    )
    if existing:
        print(f"  seat exists  {section} {seat_row}{seat_number}")
        return existing
    try:
        seat = SeatRepo.create(
            CreateSeat(
                section=section,
                seat_row=seat_row,
                seat_number=seat_number,
                venue_id=venue_id,
            )
        )
    except IntegrityError:
        print(f"  seat skipped {section} {seat_row}{seat_number} (conflict)")
        return None
    print(f"  seat created {seat.section} {seat.seat_row}{seat.seat_number} (id={seat.id})")
    return seat


def _get_or_create_event(name: str, venue_id: int, starts_at: int, ends_at: int):
    existing = next((event for event in EventRepo.get() if event.name == name), None)
    if existing:
        print(f"  event exists  {name}")
        return existing
    try:
        event = EventRepo.create(
            CreateEvent(
                name=name,
                venue_id=venue_id,
                starts_at=starts_at,
                ends_at=ends_at,
            )
        )
    except IntegrityError:
        print(f"  event skipped {name} (conflict)")
        return None
    print(f"  event created {event.name} (id={event.id})")
    return event


def _get_or_create_ticket_type(tier: str, event_id: int):
    existing = next(
        (
            ticket_type
            for ticket_type in TicketTypeRepo.get()
            if ticket_type.event_id == event_id and ticket_type.tier == tier
        ),
        None,
    )
    if existing:
        print(f"    type exists  {tier}")
        return existing
    try:
        ticket_type = TicketTypeRepo.create(
            CreateTicketType(tier=tier, event_id=event_id)
        )
    except IntegrityError:
        print(f"    type skipped {tier} (conflict)")
        return None
    print(f"    type created {ticket_type.tier} (id={ticket_type.id})")
    return ticket_type


def _get_or_create_ticket(
    price: int, seat_id: int, event_id: int, ticket_type_id: int, label: str
):
    existing = next(
        (
            ticket
            for ticket in TicketRepo.get()
            if ticket.event_id == event_id and ticket.seat_id == seat_id
        ),
        None,
    )
    if existing:
        print(f"    ticket exists  {label}")
        return existing
    try:
        ticket = TicketRepo.create(
            CreateTicket(
                price=price,
                seat_id=seat_id,
                event_id=event_id,
                ticket_type_id=ticket_type_id,
            )
        )
    except IntegrityError:
        print(f"    ticket skipped {label} (conflict)")
        return None
    print(f"    ticket created {label} (id={ticket.id}, ${price / 100:.2f})")
    return ticket


def main() -> None:
    migrate()
    now = int(time.time())
    day = 24 * 3600
    hour = 3600

    for venue_spec in VENUES:
        venue = _get_or_create_venue(
            venue_spec["name"],
            venue_spec["timezone"],
            venue_spec["address"],
        )
        if venue is None or venue.id is None:
            continue

        seats = []
        for seat_spec in SEATS:
            seat = _get_or_create_seat(
                seat_spec["section"],
                seat_spec["seat_row"],
                seat_spec["seat_number"],
                venue.id,
            )
            if seat is not None and seat.id is not None:
                seats.append((seat, seat_spec["vip"]))

        for name, days_out, hours in venue_spec["events"]:
            starts_at = now + days_out * day
            event = _get_or_create_event(
                name, venue.id, starts_at, starts_at + hours * hour
            )
            if event is None or event.id is None:
                continue

            types_by_tier = {}
            for tier, _price in TIERS:
                ticket_type = _get_or_create_ticket_type(tier, event.id)
                if ticket_type is not None and ticket_type.id is not None:
                    types_by_tier[tier] = ticket_type

            vip_type = types_by_tier.get("VIP")
            ga_type = types_by_tier.get("General Admission")
            prices = dict(TIERS)
            for seat, is_vip in seats:
                ticket_type = vip_type if is_vip else ga_type
                if ticket_type is None:
                    continue
                label = f"{seat.section} {seat.seat_row}{seat.seat_number} {ticket_type.tier}"
                _get_or_create_ticket(
                    prices[ticket_type.tier],
                    seat.id,
                    event.id,
                    ticket_type.id,
                    label,
                )


if __name__ == "__main__":
    main()
