import { useEffect, useState, type ReactNode } from "react";
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
import { FormModal, type Field } from "../components/FormModal";
import {
  formatMoney,
  formatWhen,
  fromDatetimeLocal,
  localTimezone,
  nowUnix,
  seatLabel,
  timezoneOptions,
  toDatetimeLocal,
} from "../lib/format";

type Tab = "house" | "events" | "inventory" | "people" | "tax";

type Creatable =
  | "venue"
  | "seat"
  | "event"
  | "ticket-type"
  | "ticket"
  | "user"
  | "tax-rate";

type CreateConfig = {
  title: string;
  description: string;
  submitLabel: string;
  fields: Field[];
  submit: (data: FormData) => Promise<string>;
};

export function ManagePage() {
  const [tab, setTab] = useState<Tab>("house");
  const [creating, setCreating] = useState<Creatable | null>(null);
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

  const venueName = (venueId: number) =>
    venues.find((venue) => venue.id === venueId)?.name ?? `Venue #${venueId}`;
  const eventName = (eventId: number) =>
    events.find((event) => event.id === eventId)?.name ?? `Event #${eventId}`;

  const venueOptions = venues.map((venue) => ({
    value: String(venue.id),
    label: venue.name,
  }));
  const eventOptions = events.map((event) => ({
    value: String(event.id),
    label: event.name,
  }));

  function configFor(kind: Creatable): CreateConfig {
    switch (kind) {
      case "venue":
        return {
          title: "New venue",
          description: "The building that hosts events and owns its seats.",
          submitLabel: "Create venue",
          fields: [
            { kind: "text", name: "name", label: "Name", placeholder: "The Grand Hall" },
            {
              kind: "select",
              name: "timezone",
              label: "Timezone",
              placeholder: "Choose a timezone",
              options: timezoneOptions(),
              defaultValue: localTimezone(),
            },
            {
              kind: "text",
              name: "address",
              label: "Address",
              placeholder: "100 Broadway, New York, NY",
            },
          ],
          submit: async (data) => {
            const venue = await api.post<Venue>("/venues/", {
              name: data.get("name"),
              timezone: data.get("timezone"),
              address: data.get("address"),
            });
            return `Created venue “${venue.name}”.`;
          },
        };
      case "seat":
        return {
          title: "New seat",
          description: "Seats belong to a venue and are reused across events.",
          submitLabel: "Create seat",
          fields: [
            {
              kind: "select",
              name: "venue_id",
              label: "Venue",
              placeholder: "Choose a venue",
              options: venueOptions,
            },
            {
              kind: "text",
              name: "section",
              label: "Section",
              placeholder: "Orchestra",
            },
            { kind: "text", name: "seat_row", label: "Row", placeholder: "A" },
            { kind: "text", name: "seat_number", label: "Number", placeholder: "1" },
          ],
          submit: async (data) => {
            const seat = await api.post<Seat>("/seats/", {
              section: data.get("section"),
              seat_row: data.get("seat_row"),
              seat_number: data.get("seat_number"),
              venue_id: Number(data.get("venue_id")),
            });
            return `Created seat ${seatLabel(seat)}.`;
          },
        };
      case "event":
        return {
          title: "New event",
          description: "A dated performance at one of your venues.",
          submitLabel: "Create event",
          fields: [
            {
              kind: "text",
              name: "name",
              label: "Event name",
              placeholder: "Late Set at the Grand Hall",
            },
            {
              kind: "select",
              name: "venue_id",
              label: "Venue",
              placeholder: "Choose a venue",
              options: venueOptions,
            },
            {
              kind: "datetime",
              name: "starts_at",
              label: "Starts",
              defaultValue: toDatetimeLocal(nowUnix() + 86400),
            },
            {
              kind: "datetime",
              name: "ends_at",
              label: "Ends",
              defaultValue: toDatetimeLocal(nowUnix() + 86400 + 7200),
            },
          ],
          submit: async (data) => {
            const event = await api.post<Event>("/events/", {
              name: data.get("name"),
              venue_id: Number(data.get("venue_id")),
              starts_at: fromDatetimeLocal(String(data.get("starts_at"))),
              ends_at: fromDatetimeLocal(String(data.get("ends_at"))),
            });
            return `Created event “${event.name}”.`;
          },
        };
      case "ticket-type":
        return {
          title: "New ticket type",
          description: "A pricing tier for one event, such as VIP or GA.",
          submitLabel: "Create ticket type",
          fields: [
            {
              kind: "select",
              name: "event_id",
              label: "Event",
              placeholder: "Choose an event",
              options: eventOptions,
            },
            { kind: "text", name: "tier", label: "Tier", placeholder: "VIP" },
          ],
          submit: async (data) => {
            const type = await api.post<TicketType>("/ticket-types/", {
              tier: data.get("tier"),
              event_id: Number(data.get("event_id")),
            });
            return `Created ${type.tier} tier for ${eventName(type.event_id)}.`;
          },
        };
      case "ticket":
        return {
          title: "New ticket",
          description: "One sellable seat at a given tier and price.",
          submitLabel: "Create ticket",
          fields: [
            {
              kind: "select",
              name: "ticket_type_id",
              label: "Ticket type",
              placeholder: "Choose a ticket type",
              options: ticketTypes.map((type) => ({
                value: String(type.id),
                label: `${type.tier} · ${eventName(type.event_id)}`,
              })),
            },
            {
              kind: "select",
              name: "seat_id",
              label: "Seat",
              placeholder: "Choose a seat",
              options: seats.map((seat) => ({
                value: String(seat.id),
                label: `${seatLabel(seat)} · ${venueName(seat.venue_id)}`,
              })),
            },
            {
              kind: "number",
              name: "price",
              label: "Price in dollars",
              placeholder: "45.00",
              min: "0",
              step: "0.01",
            },
          ],
          submit: async (data) => {
            const ticket = await api.post<Ticket>("/tickets/", {
              price: Math.round(Number(data.get("price")) * 100),
              seat_id: Number(data.get("seat_id")),
              ticket_type_id: Number(data.get("ticket_type_id")),
            });
            const seat = seats.find((item) => item.id === ticket.seat_id);
            return `Created ${formatMoney(ticket.price)} ticket for ${
              seat ? seatLabel(seat) : `seat #${ticket.seat_id}`
            }.`;
          },
        };
      case "user":
        return {
          title: "New buyer",
          description: "Buyers are attached to orders at checkout.",
          submitLabel: "Create buyer",
          fields: [
            { kind: "text", name: "name", label: "Name", placeholder: "Alex Rivera" },
            {
              kind: "email",
              name: "email",
              label: "Email",
              placeholder: "alex@example.com",
            },
          ],
          submit: async (data) => {
            const user = await api.post<User>("/users/", {
              name: data.get("name"),
              email: data.get("email"),
            });
            return `Created buyer ${user.name}.`;
          },
        };
      case "tax-rate":
        return {
          title: "New tax rate",
          description: "Applied to the subtotal when an order is placed.",
          submitLabel: "Create tax rate",
          fields: [
            {
              kind: "text",
              name: "jurisdiction",
              label: "Jurisdiction",
              placeholder: "NY",
            },
            { kind: "text", name: "tax_type", label: "Tax type", placeholder: "sales" },
            {
              kind: "number",
              name: "percent",
              label: "Percent",
              placeholder: "8.875",
              min: "0",
              step: "0.001",
            },
            {
              kind: "datetime",
              name: "effective_from",
              label: "Effective from",
              defaultValue: toDatetimeLocal(nowUnix()),
            },
          ],
          submit: async (data) => {
            const rate = await api.post<TaxRate>("/tax-rates/", {
              jurisdiction: data.get("jurisdiction"),
              tax_type: data.get("tax_type"),
              rate: Number(data.get("percent")) / 100,
              effective_from: fromDatetimeLocal(String(data.get("effective_from"))),
            });
            return `Created ${rate.jurisdiction} ${rate.tax_type} rate at ${(
              rate.rate * 100
            ).toFixed(3)}%.`;
          },
        };
    }
  }

  function openCreate(kind: Creatable) {
    setMessage(null);
    setError(null);
    setCreating(kind);
  }

  async function handleCreate(config: CreateConfig, data: FormData) {
    const summary = await config.submit(data);
    await refresh();
    setCreating(null);
    setMessage(summary);
  }

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
      setMessage("Sample house loaded. Switch to the attendee view to buy a seat.");
    } catch (err) {
      setError(
        err instanceof Error
          ? `${err.message} (If the sample house already exists, create records individually instead.)`
          : "Seed failed",
      );
    } finally {
      setBusy(false);
    }
  }

  const config = creating ? configFor(creating) : null;

  return (
    <section>
      <div className="page-head">
        <p className="eyebrow">Organizer workspace</p>
        <h1>Run the box office</h1>
        <p>Stock the house: venues, seats, events, tickets, buyers, and tax.</p>
      </div>
      <div className="toolbar">
        <button
          type="button"
          className="ghost"
          disabled={busy}
          onClick={() => void seedHouse()}
        >
          {busy ? "Seeding…" : "Load sample house"}
        </button>
        <button type="button" className="ghost" onClick={() => void refresh()}>
          Refresh
        </button>
      </div>
      {message && <p className="banner success">{message}</p>}
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
        <div className="split">
          <Collection
            title="Venues"
            count={venues.length}
            actionLabel="New venue"
            onNew={() => openCreate("venue")}
            empty="No venues yet. Create one to start building the house."
          >
            {venues.map((venue) => (
              <li key={venue.id}>
                <div>
                  <strong>{venue.name}</strong>
                  <span>
                    {venue.address} · {venue.timezone}
                  </span>
                </div>
              </li>
            ))}
          </Collection>
          <Collection
            title="Seats"
            count={seats.length}
            actionLabel="New seat"
            onNew={() => openCreate("seat")}
            empty="No seats yet. Seats are what tickets are sold against."
          >
            {seats.map((seat) => (
              <li key={seat.id}>
                <div>
                  <strong>{seatLabel(seat)}</strong>
                  <span>{venueName(seat.venue_id)}</span>
                </div>
              </li>
            ))}
          </Collection>
        </div>
      )}

      {tab === "events" && (
        <Collection
          title="Events"
          count={events.length}
          actionLabel="New event"
          onNew={() => openCreate("event")}
          empty="No events yet. Attendees only see events that exist here."
        >
          {events.map((event) => (
            <li key={event.id}>
              <div>
                <strong>{event.name}</strong>
                <span>
                  {venueName(event.venue_id)} · {formatWhen(event.starts_at)}
                </span>
              </div>
            </li>
          ))}
        </Collection>
      )}

      {tab === "inventory" && (
        <div className="split">
          <Collection
            title="Ticket types"
            count={ticketTypes.length}
            actionLabel="New ticket type"
            onNew={() => openCreate("ticket-type")}
            empty="No tiers yet. Every ticket needs a type."
          >
            {ticketTypes.map((type) => (
              <li key={type.id}>
                <div>
                  <strong>{type.tier}</strong>
                  <span>{eventName(type.event_id)}</span>
                </div>
              </li>
            ))}
          </Collection>
          <Collection
            title="Tickets"
            count={tickets.length}
            actionLabel="New ticket"
            onNew={() => openCreate("ticket")}
            empty="No tickets yet. Nothing is on sale until you add some."
          >
            {tickets.map((ticket) => {
              const seat = seats.find((item) => item.id === ticket.seat_id);
              const type = ticketTypes.find(
                (item) => item.id === ticket.ticket_type_id,
              );
              return (
                <li key={ticket.id}>
                  <div>
                    <strong>{seat ? seatLabel(seat) : `Seat #${ticket.seat_id}`}</strong>
                    <span>
                      {type?.tier ?? `Type #${ticket.ticket_type_id}`} ·{" "}
                      {formatMoney(ticket.price)}
                    </span>
                  </div>
                  <em className={ticket.sold_at ? "sold" : "available"}>
                    {ticket.sold_at ? "Sold" : "Available"}
                  </em>
                </li>
              );
            })}
          </Collection>
        </div>
      )}

      {tab === "people" && (
        <Collection
          title="Buyers"
          count={users.length}
          actionLabel="New buyer"
          onNew={() => openCreate("user")}
          empty="No buyers yet. One is needed to place an order."
        >
          {users.map((user) => (
            <li key={user.id}>
              <div>
                <strong>{user.name}</strong>
                <span>{user.email}</span>
              </div>
            </li>
          ))}
        </Collection>
      )}

      {tab === "tax" && (
        <Collection
          title="Tax rates"
          count={taxRates.length}
          actionLabel="New tax rate"
          onNew={() => openCreate("tax-rate")}
          empty="No tax rates yet. Checkout needs at least one."
        >
          {taxRates.map((rate) => (
            <li key={rate.id}>
              <div>
                <strong>
                  {rate.jurisdiction} {rate.tax_type}
                </strong>
                <span>Effective {formatWhen(rate.effective_from)}</span>
              </div>
              <em>{(rate.rate * 100).toFixed(3)}%</em>
            </li>
          ))}
        </Collection>
      )}

      {config && (
        <FormModal
          key={creating}
          title={config.title}
          description={config.description}
          fields={config.fields}
          submitLabel={config.submitLabel}
          onSubmit={(data) => handleCreate(config, data)}
          onClose={() => setCreating(null)}
        />
      )}
    </section>
  );
}

function Collection({
  title,
  count,
  actionLabel,
  onNew,
  empty,
  children,
}: {
  title: string;
  count: number;
  actionLabel: string;
  onNew: () => void;
  empty: string;
  children: ReactNode;
}) {
  return (
    <article className="panel">
      <header className="panel-head">
        <div>
          <h2>{title}</h2>
          <p className="hint">{count === 0 ? "Nothing yet" : `${count} total`}</p>
        </div>
        <button type="button" className="primary" onClick={onNew}>
          {actionLabel}
        </button>
      </header>
      {count === 0 ? (
        <p className="empty">{empty}</p>
      ) : (
        <ul className="plain-list">{children}</ul>
      )}
    </article>
  );
}
