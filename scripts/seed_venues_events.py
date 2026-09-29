from __future__ import annotations

from datetime import datetime, timedelta, timezone

from psycopg import IntegrityError

from api.dto.requests.event import CreateEvent
from api.dto.requests.order import CreateOrder
from api.dto.requests.order_item import CreateOrderItem
from api.dto.requests.seat import CreateSeat
from api.dto.requests.tax_rate import CreateTaxRate
from api.dto.requests.ticket import CreateTicket, UpdateTicket
from api.dto.requests.ticket_type import CreateTicketType
from api.dto.requests.user import CreateUser
from api.dto.requests.venue import CreateVenue
from api.rest.repos.event import EventRepo
from api.rest.repos.order import OrderRepo
from api.rest.repos.order_item import OrderItemRepo
from api.rest.repos.seat import SeatRepo
from api.rest.repos.tax_rate import TaxRateRepo
from api.rest.repos.ticket import TicketRepo
from api.rest.repos.ticket_type import TicketTypeRepo
from api.rest.repos.user import UserRepo
from api.rest.repos.venue import VenueRepo

USERS = [
    ("Ada Lovelace", "ada@example.com"),
    ("Grace Hopper", "grace@example.com"),
    ("Alan Turing", "alan@example.com"),
    ("Katherine Johnson", "katherine@example.com"),
    ("Donald Knuth", "donald@example.com"),
]

TAX_RATES = [
    ("NY", "sales", 0.08875),
    ("CA", "sales", 0.0975),
    ("IL", "sales", 0.1025),
    ("TX", "sales", 0.0825),
    ("GB", "vat", 0.20),
]

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
        "jurisdiction": "NY",
        "events": [("Late Set at the Grand Hall", 7, 3), ("Sunday Matinee", 14, 2)],
    },
    {
        "name": "The Fillmore",
        "timezone": "America/Los_Angeles",
        "address": "1805 Geary Blvd, San Francisco, CA",
        "jurisdiction": "CA",
        "events": [("West Coast Double Bill", 10, 4)],
    },
    {
        "name": "Royal Albert Hall",
        "timezone": "Europe/London",
        "address": "Kensington Gore, London",
        "jurisdiction": "GB",
        "events": [("Proms Chamber Night", 21, 3), ("Organ Recital", 28, 2)],
    },
    {
        "name": "Chicago Theatre",
        "timezone": "America/Chicago",
        "address": "175 N State St, Chicago, IL",
        "jurisdiction": "IL",
        "events": [("Windy City Jazz Night", 5, 3)],
    },
    {
        "name": "Austin City Limits Live",
        "timezone": "America/Chicago",
        "address": "310 Willie Nelson Blvd, Austin, TX",
        "jurisdiction": "TX",
        "events": [("ACL Studio Session", 12, 2)],
    },
    {
        "name": "Beacon Theatre",
        "timezone": "America/New_York",
        "address": "2124 Broadway, New York, NY",
        "jurisdiction": "NY",
        "events": [("Uptown Acoustic Evening", 9, 2)],
    },
    {
        "name": "The Greek Theatre",
        "timezone": "America/Los_Angeles",
        "address": "2700 N Vermont Ave, Los Angeles, CA",
        "jurisdiction": "CA",
        "events": [("Hillside Summer Show", 16, 3)],
    },
    {
        "name": "Symphony Center",
        "timezone": "America/Chicago",
        "address": "220 S Michigan Ave, Chicago, IL",
        "jurisdiction": "IL",
        "events": [("CSO Chamber Series", 18, 2)],
    },
    {
        "name": "Bass Concert Hall",
        "timezone": "America/Chicago",
        "address": "2350 Robert Dedman Dr, Austin, TX",
        "jurisdiction": "TX",
        "events": [("Longhorn Arts Showcase", 11, 3)],
    },
    {
        "name": "Barbican Centre",
        "timezone": "Europe/London",
        "address": "Silk St, London",
        "jurisdiction": "GB",
        "events": [("Barbican Contemporary Night", 25, 2)],
    },
]

# (buyer email, venue name, event name, seat labels like "A1")
SALES = [
    ("ada@example.com", "The Grand Hall", "Late Set at the Grand Hall", ["A1", "A2"]),
    ("grace@example.com", "The Fillmore", "West Coast Double Bill", ["B1"]),
    ("alan@example.com", "Chicago Theatre", "Windy City Jazz Night", ["A3"]),
    ("katherine@example.com", "Royal Albert Hall", "Proms Chamber Night", ["B2", "B3"]),
]

# (holder email, venue name, event name, seat label)
HOLDS = [
    ("donald@example.com", "Beacon Theatre", "Uptown Acoustic Evening", "A4"),
    ("ada@example.com", "Austin City Limits Live", "ACL Studio Session", "B4"),
]


def _get_or_create_user(name: str, email: str):
    existing = next((user for user in UserRepo.get() if user.email == email), None)
    if existing:
        print(f"user exists  {email}")
        return existing
    user = UserRepo.create(CreateUser(name=name, email=email))
    print(f"user created {user.name} (id={user.id})")
    return user


def _get_or_create_tax_rate(
    jurisdiction: str, tax_type: str, rate: float, effective_from: datetime
):
    existing = next(
        (
            tax_rate
            for tax_rate in TaxRateRepo.get()
            if tax_rate.jurisdiction == jurisdiction
            and tax_rate.tax_type == tax_type
            and tax_rate.effective_to is None
        ),
        None,
    )
    if existing:
        print(f"tax exists   {jurisdiction} {tax_type}")
        return existing
    try:
        tax_rate = TaxRateRepo.create(
            CreateTaxRate(
                jurisdiction=jurisdiction,
                tax_type=tax_type,
                rate=rate,
                effective_from=effective_from,
            )
        )
    except IntegrityError:
        print(f"tax skipped  {jurisdiction} {tax_type} (conflict)")
        return None
    print(f"tax created  {tax_rate.jurisdiction} {tax_rate.tax_type} ({tax_rate.rate})")
    return tax_rate


def _get_or_create_venue(name: str, timezone_name: str, address: str):
    existing = next((venue for venue in VenueRepo.get() if venue.name == name), None)
    if existing:
        print(f"venue exists  {name}")
        return existing
    venue = VenueRepo.create(
        CreateVenue(name=name, timezone=timezone_name, address=address)
    )
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


def _get_or_create_event(name: str, venue_id: int, starts_at: datetime, ends_at: datetime):
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


def _find_ticket(event_id: int, seat_row: str, seat_number: str):
    seats = {seat.id: seat for seat in SeatRepo.get()}
    for ticket in TicketRepo.get():
        if ticket.event_id != event_id:
            continue
        seat = seats.get(ticket.seat_id)
        if seat and seat.seat_row == seat_row and seat.seat_number == seat_number:
            return ticket
    return None


def _seed_sale(
    buyer_email: str,
    venue_name: str,
    event_name: str,
    seat_labels: list[str],
    users_by_email: dict,
    venues_by_name: dict,
    events_by_name: dict,
    tax_by_jurisdiction: dict,
    venue_jurisdiction: dict[str, str],
    sold_at: datetime,
):
    buyer = users_by_email.get(buyer_email)
    venue = venues_by_name.get(venue_name)
    event = events_by_name.get(event_name)
    if buyer is None or venue is None or event is None:
        print(f"sale skipped missing refs for {event_name}")
        return

    existing_order_ticket_ids = {item.ticket_id for item in OrderItemRepo.get()}
    tickets = []
    for label in seat_labels:
        seat_row, seat_number = label[0], label[1:]
        ticket = _find_ticket(event.id, seat_row, seat_number)
        if ticket is None:
            print(f"sale skipped missing ticket {event_name} {label}")
            return
        if ticket.sold_at is not None or ticket.id in existing_order_ticket_ids:
            print(f"sale exists  {buyer_email} {event_name} {label}")
            return
        tickets.append(ticket)

    jurisdiction = venue_jurisdiction[venue_name]
    tax_rate = tax_by_jurisdiction.get(jurisdiction)
    if tax_rate is None:
        print(f"sale skipped missing tax for {jurisdiction}")
        return

    subtotal = sum(ticket.price for ticket in tickets)
    tax_amount = int(round(subtotal * tax_rate.rate))
    order = OrderRepo.create(
        CreateOrder(
            status="paid",
            user_id=buyer.id,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_charged=subtotal + tax_amount,
            tax_rate_applied=tax_rate.rate,
            tax_jurisdiction=jurisdiction,
        )
    )
    print(
        f"order created id={order.id} buyer={buyer_email} "
        f"${(subtotal + tax_amount) / 100:.2f}"
    )

    for ticket in tickets:
        OrderItemRepo.create(CreateOrderItem(order_id=order.id, ticket_id=ticket.id))
        TicketRepo.update_by_id(
            ticket.id,
            UpdateTicket(
                sold_at=sold_at,
                sold_to_user_id=buyer.id,
                held_until=None,
                held_by_user_id=None,
            ),
        )
        print(f"  sold ticket id={ticket.id}")


def _seed_hold(
    holder_email: str,
    venue_name: str,
    event_name: str,
    seat_label: str,
    users_by_email: dict,
    events_by_name: dict,
    held_until: datetime,
):
    holder = users_by_email.get(holder_email)
    event = events_by_name.get(event_name)
    if holder is None or event is None:
        print(f"hold skipped missing refs for {event_name}")
        return

    seat_row, seat_number = seat_label[0], seat_label[1:]
    ticket = _find_ticket(event.id, seat_row, seat_number)
    if ticket is None:
        print(f"hold skipped missing ticket {event_name} {seat_label}")
        return
    if ticket.sold_at is not None:
        print(f"hold skipped sold ticket {event_name} {seat_label}")
        return
    if ticket.held_by_user_id is not None:
        print(f"hold exists  {holder_email} {event_name} {seat_label}")
        return

    TicketRepo.update_by_id(
        ticket.id,
        UpdateTicket(held_until=held_until, held_by_user_id=holder.id),
    )
    print(f"hold created {holder_email} {event_name} {seat_label} until {held_until.isoformat()}")


def main() -> None:
    now = datetime.now(timezone.utc)

    users_by_email = {}
    for name, email in USERS:
        user = _get_or_create_user(name, email)
        if user is not None and user.id is not None:
            users_by_email[email] = user

    tax_by_jurisdiction = {}
    for jurisdiction, tax_type, rate in TAX_RATES:
        tax_rate = _get_or_create_tax_rate(
            jurisdiction, tax_type, rate, now - timedelta(days=30)
        )
        if tax_rate is not None:
            tax_by_jurisdiction[jurisdiction] = tax_rate

    venues_by_name = {}
    events_by_name = {}
    venue_jurisdiction = {}

    for venue_spec in VENUES:
        venue = _get_or_create_venue(
            venue_spec["name"],
            venue_spec["timezone"],
            venue_spec["address"],
        )
        if venue is None or venue.id is None:
            continue
        venues_by_name[venue.name] = venue
        venue_jurisdiction[venue.name] = venue_spec["jurisdiction"]

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
            starts_at = now + timedelta(days=days_out)
            event = _get_or_create_event(
                name, venue.id, starts_at, starts_at + timedelta(hours=hours)
            )
            if event is None or event.id is None:
                continue
            events_by_name[event.name] = event

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

    print("--- sales ---")
    for buyer_email, venue_name, event_name, seat_labels in SALES:
        _seed_sale(
            buyer_email,
            venue_name,
            event_name,
            seat_labels,
            users_by_email,
            venues_by_name,
            events_by_name,
            tax_by_jurisdiction,
            venue_jurisdiction,
            now - timedelta(hours=2),
        )

    print("--- holds ---")
    for holder_email, venue_name, event_name, seat_label in HOLDS:
        _seed_hold(
            holder_email,
            venue_name,
            event_name,
            seat_label,
            users_by_email,
            events_by_name,
            now + timedelta(minutes=15),
        )


if __name__ == "__main__":
    main()
