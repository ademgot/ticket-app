import { type FormEvent, useEffect, useState } from "react";
import { api } from "../api/client";
import type {
  Event,
  Seat,
  TaxRate,
  Ticket,
  TicketType,
  User,
  Venue,
} from "../api/types";
import { fromDatetimeLocal, nowUnix, toDatetimeLocal } from "../lib/format";

type Tab =
  | "house"
  | "events"
  | "inventory"
  | "people"
  | "tax";

export function ManagePage() {
  const [tab, setTab] = useState<Tab>("house");
  const [venues, setVenues] = useState<Venue[]>([]);
  const [seats, setSeats] = useState<Seat[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [ticketTypes, setTicketTypes] = useState<TicketType[]>([]);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [taxRates, setTaxRates] = useState<TaxRate[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function refresh() {
    const [
      venueList,
      seatList,
      eventList,
      typeList,
      ticketList,
      userList,
      rateList,
    ] = await Promise.all([
      api.get<Venue[]>("/venues/"),
      api.get<Seat[]>("/seats/"),
      api.get<Event[]>("/events/"),
      api.get<TicketType[]>("/ticket-types/"),
      api.get<Ticket[]>("/tickets/"),
      api.get<User[]>("/users/"),
      api.get<TaxRate[]>("/tax-rates/"),
    ]);
    setVenues(venueList);
    setSeats(seatList);
    setEvents(eventList);
    setTicketTypes(typeList);
    setTickets(ticketList);
    setUsers(userList);
    setTaxRates(rateList);
  }

  useEffect(() => {
    refresh().catch((err: Error) => setError(err.message));
  }, []);

  async function seedHouse() {
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      const venue = await api.post<Venue>("/venues/", {
        name: "The Grand Hall",
        timezone: "America/New_York",
        address: "100 Broadway, New York, NY",
      });
      const seatSpecs = ["A", "B"].flatMap((row) =>
        ["1", "2", "3", "4"].map((number) => ({
          section: "Orchestra",
          seat_row: row,
          seat_number: number,
          venue_id: venue.id,
        })),
      );
      const createdSeats: Seat[] = [];
      for (const spec of seatSpecs) {
        createdSeats.push(await api.post<Seat>("/seats/", spec));
      }
      const start = nowUnix() + 86400 * 7;
      const event = await api.post<Event>("/events/", {
        name: "Late Set at the Grand Hall",
        venue_id: venue.id,
        starts_at: start,
        ends_at: start + 3 * 3600,
      });
      const ga = await api.post<TicketType>("/ticket-types/", {
        tier: "General Admission",
        event_id: event.id,
      });
      const vip = await api.post<TicketType>("/ticket-types/", {
        tier: "VIP",
        event_id: event.id,
      });
      for (const [index, seat] of createdSeats.entries()) {
        const vipSeat = index < 4;
        await api.post<Ticket>("/tickets/", {
          price: vipSeat ? 12500 : 4500,
          seat_id: seat.id,
          ticket_type_id: vipSeat ? vip.id : ga.id,
        });
      }
      await api.post<User>("/users/", {
        name: "Alex Rivera",
        email: "alex@example.com",
      });
      await api.post<TaxRate>("/tax-rates/", {
        jurisdiction: "NY",
        tax_type: "sales",
        rate: 0.08875,
        effective_from: nowUnix() - 86400,
      });
      await refresh();
      setMessage("Sample house loaded. Open Events to buy a seat.");
    } catch (err) {
      setError(
        err instanceof Error
          ? `${err.message} (If the house already exists, skip seed and use the forms.)`
          : "Seed failed",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <section>
      <div className="page-head">
        <h1>Manage</h1>
        <p>Stock the house: venues, seats, events, tickets, buyers, and tax.</p>
      </div>
      <div className="toolbar">
        <button type="button" className="primary" disabled={busy} onClick={() => void seedHouse()}>
          {busy ? "Seeding…" : "Load sample house"}
        </button>
        <button type="button" className="ghost" onClick={() => void refresh()}>
          Refresh
        </button>
      </div>
      {message && <p className="banner">{message}</p>}
      {error && <p className="banner error">{error}</p>}
      <div className="tabs">
        {(
          [
            ["house", "Venues & seats"],
            ["events", "Events"],
            ["inventory", "Tickets"],
            ["people", "Buyers"],
            ["tax", "Tax"],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            className={tab === id ? "tab active" : "tab"}
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </div>
      {tab === "house" && (
        <HouseForms venues={venues} seats={seats} onChange={() => void refresh()} />
      )}
      {tab === "events" && (
        <EventForms venues={venues} events={events} onChange={() => void refresh()} />
      )}
      {tab === "inventory" && (
        <InventoryForms
          events={events}
          seats={seats}
          ticketTypes={ticketTypes}
          tickets={tickets}
          onChange={() => void refresh()}
        />
      )}
      {tab === "people" && <PeopleForms users={users} onChange={() => void refresh()} />}
      {tab === "tax" && <TaxForms rates={taxRates} onChange={() => void refresh()} />}
    </section>
  );
}

function HouseForms({
  venues,
  seats,
  onChange,
}: {
  venues: Venue[];
  seats: Seat[];
  onChange: () => void;
}) {
  const [venueId, setVenueId] = useState("");

  async function createVenue(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await api.post("/venues/", {
      name: form.get("name"),
      timezone: form.get("timezone"),
      address: form.get("address"),
    });
    event.currentTarget.reset();
    onChange();
  }

  async function createSeat(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await api.post("/seats/", {
      section: form.get("section"),
      seat_row: form.get("seat_row"),
      seat_number: form.get("seat_number"),
      venue_id: Number(form.get("venue_id")),
    });
    event.currentTarget.reset();
    onChange();
  }

  return (
    <div className="split">
      <form className="panel" onSubmit={(event) => void createVenue(event)}>
        <h2>New venue</h2>
        <input name="name" placeholder="Name" required />
        <input name="timezone" placeholder="America/New_York" required />
        <input name="address" placeholder="Address" required />
        <button type="submit" className="primary">
          Save venue
        </button>
        <ul className="plain-list">
          {venues.map((venue) => (
            <li key={venue.id}>
              <strong>{venue.name}</strong>
              <span>
                {venue.address} · {venue.timezone}
              </span>
            </li>
          ))}
        </ul>
      </form>
      <form className="panel" onSubmit={(event) => void createSeat(event)}>
        <h2>New seat</h2>
        <select
          name="venue_id"
          value={venueId}
          onChange={(event) => setVenueId(event.target.value)}
          required
        >
          <option value="">Venue</option>
          {venues.map((venue) => (
            <option key={venue.id} value={venue.id}>
              {venue.name}
            </option>
          ))}
        </select>
        <input name="section" placeholder="Section" required />
        <input name="seat_row" placeholder="Row" required />
        <input name="seat_number" placeholder="Number" required />
        <button type="submit" className="primary">
          Save seat
        </button>
        <ul className="plain-list">
          {seats.map((seat) => (
            <li key={seat.id}>
              {seat.section} {seat.seat_row}-{seat.seat_number}
              <span>
                {venues.find((venue) => venue.id === seat.venue_id)?.name ??
                  `Venue #${seat.venue_id}`}
              </span>
            </li>
          ))}
        </ul>
      </form>
    </div>
  );
}

function EventForms({
  venues,
  events,
  onChange,
}: {
  venues: Venue[];
  events: Event[];
  onChange: () => void;
}) {
  async function createEvent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await api.post("/events/", {
      name: form.get("name"),
      venue_id: Number(form.get("venue_id")),
      starts_at: fromDatetimeLocal(String(form.get("starts_at"))),
      ends_at: fromDatetimeLocal(String(form.get("ends_at"))),
    });
    event.currentTarget.reset();
    onChange();
  }

  return (
    <form className="panel" onSubmit={(event) => void createEvent(event)}>
      <h2>New event</h2>
      <input name="name" placeholder="Event name" required />
      <select name="venue_id" required defaultValue="">
        <option value="" disabled>
          Venue
        </option>
        {venues.map((venue) => (
          <option key={venue.id} value={venue.id}>
            {venue.name}
          </option>
        ))}
      </select>
      <label>
        Starts
        <input
          type="datetime-local"
          name="starts_at"
          defaultValue={toDatetimeLocal(nowUnix() + 86400)}
          required
        />
      </label>
      <label>
        Ends
        <input
          type="datetime-local"
          name="ends_at"
          defaultValue={toDatetimeLocal(nowUnix() + 86400 + 7200)}
          required
        />
      </label>
      <button type="submit" className="primary">
        Save event
      </button>
      <ul className="plain-list">
        {events.map((item) => (
          <li key={item.id}>
            <strong>{item.name}</strong>
            <span>
              {venues.find((venue) => venue.id === item.venue_id)?.name ??
                `Venue #${item.venue_id}`}
            </span>
          </li>
        ))}
      </ul>
    </form>
  );
}

function InventoryForms({
  events,
  seats,
  ticketTypes,
  tickets,
  onChange,
}: {
  events: Event[];
  seats: Seat[];
  ticketTypes: TicketType[];
  tickets: Ticket[];
  onChange: () => void;
}) {
  async function createType(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await api.post("/ticket-types/", {
      tier: form.get("tier"),
      event_id: Number(form.get("event_id")),
    });
    event.currentTarget.reset();
    onChange();
  }

  async function createTicket(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const dollars = Number(form.get("price"));
    await api.post("/tickets/", {
      price: Math.round(dollars * 100),
      seat_id: Number(form.get("seat_id")),
      ticket_type_id: Number(form.get("ticket_type_id")),
    });
    event.currentTarget.reset();
    onChange();
  }

  return (
    <div className="split">
      <form className="panel" onSubmit={(event) => void createType(event)}>
        <h2>Ticket type</h2>
        <select name="event_id" required defaultValue="">
          <option value="" disabled>
            Event
          </option>
          {events.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </select>
        <input name="tier" placeholder="VIP / GA" required />
        <button type="submit" className="primary">
          Save type
        </button>
        <ul className="plain-list">
          {ticketTypes.map((type) => (
            <li key={type.id}>
              {type.tier}
              <span>
                {events.find((item) => item.id === type.event_id)?.name ??
                  `Event #${type.event_id}`}
              </span>
            </li>
          ))}
        </ul>
      </form>
      <form className="panel" onSubmit={(event) => void createTicket(event)}>
        <h2>Inventory ticket</h2>
        <select name="ticket_type_id" required defaultValue="">
          <option value="" disabled>
            Ticket type
          </option>
          {ticketTypes.map((type) => (
            <option key={type.id} value={type.id}>
              {type.tier} (
              {events.find((item) => item.id === type.event_id)?.name ?? type.event_id})
            </option>
          ))}
        </select>
        <select name="seat_id" required defaultValue="">
          <option value="" disabled>
            Seat
          </option>
          {seats.map((seat) => (
            <option key={seat.id} value={seat.id}>
              {seat.section} {seat.seat_row}-{seat.seat_number}
            </option>
          ))}
        </select>
        <input
          name="price"
          type="number"
          min="0"
          step="0.01"
          placeholder="Price in dollars"
          required
        />
        <button type="submit" className="primary">
          Save ticket
        </button>
        <p className="hint">{tickets.length} tickets in inventory</p>
      </form>
    </div>
  );
}

function PeopleForms({
  users,
  onChange,
}: {
  users: User[];
  onChange: () => void;
}) {
  async function createUser(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await api.post("/users/", {
      name: form.get("name"),
      email: form.get("email"),
    });
    event.currentTarget.reset();
    onChange();
  }

  return (
    <form className="panel" onSubmit={(event) => void createUser(event)}>
      <h2>Buyer</h2>
      <input name="name" placeholder="Name" required />
      <input name="email" type="email" placeholder="Email" required />
      <button type="submit" className="primary">
        Save buyer
      </button>
      <ul className="plain-list">
        {users.map((user) => (
          <li key={user.id}>
            <strong>{user.name}</strong>
            <span>{user.email}</span>
          </li>
        ))}
      </ul>
    </form>
  );
}

function TaxForms({
  rates,
  onChange,
}: {
  rates: TaxRate[];
  onChange: () => void;
}) {
  async function createRate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await api.post("/tax-rates/", {
      jurisdiction: form.get("jurisdiction"),
      tax_type: form.get("tax_type"),
      rate: Number(form.get("percent")) / 100,
      effective_from: fromDatetimeLocal(String(form.get("effective_from"))),
    });
    event.currentTarget.reset();
    onChange();
  }

  return (
    <form className="panel" onSubmit={(event) => void createRate(event)}>
      <h2>Tax rate</h2>
      <input name="jurisdiction" placeholder="NY" required />
      <input name="tax_type" placeholder="sales" required />
      <input
        name="percent"
        type="number"
        min="0"
        step="0.01"
        placeholder="Percent, e.g. 8.875"
        required
      />
      <label>
        Effective from
        <input
          type="datetime-local"
          name="effective_from"
          defaultValue={toDatetimeLocal(nowUnix())}
          required
        />
      </label>
      <button type="submit" className="primary">
        Save rate
      </button>
      <ul className="plain-list">
        {rates.map((rate) => (
          <li key={rate.id}>
            {rate.jurisdiction} {rate.tax_type}
            <span>{(rate.rate * 100).toFixed(3)}%</span>
          </li>
        ))}
      </ul>
    </form>
  );
}
