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
import { ConfirmModal, FormModal, type Field } from "../components/FormModal";
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

type Tab = "house" | "events" | "people" | "tax";

type EntityKind =
  | "venue"
  | "seat"
  | "event"
  | "ticket-type"
  | "ticket"
  | "user"
  | "tax-rate";

type EntityRecord = Venue | Seat | Event | TicketType | Ticket | User | TaxRate;

type FormConfig = {
  title: string;
  description: string;
  submitLabel: string;
  fields: Field[];
  submit: (data: FormData) => Promise<string>;
};

type Dialog =
  | { action: "create"; kind: EntityKind }
  | { action: "edit"; kind: EntityKind; record: EntityRecord }
  | { action: "delete"; kind: EntityKind; id: number; label: string };

const DELETE_PATH: Record<EntityKind, (id: number) => string> = {
  venue: (id) => `/venues/${id}`,
  seat: (id) => `/seats/${id}`,
  event: (id) => `/events/${id}`,
  "ticket-type": (id) => `/ticket-types/${id}`,
  ticket: (id) => `/tickets/${id}`,
  user: (id) => `/users/${id}`,
  "tax-rate": (id) => `/tax-rates/${id}`,
};

export function ManagePage() {
  const [tab, setTab] = useState<Tab>("house");
  const [inventoryVenueId, setInventoryVenueId] = useState<number | null>(null);
  const [inventoryEventId, setInventoryEventId] = useState<number | null>(null);
  const [dialog, setDialog] = useState<Dialog | null>(null);
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
  const inventoryVenue =
    venues.find((venue) => venue.id === inventoryVenueId) ?? null;
  const venueSeats = seats.filter(
    (seat) => seat.venue_id === inventoryVenueId,
  );
  const inventoryEvent =
    events.find((event) => event.id === inventoryEventId) ?? null;
  const eventTicketTypes = ticketTypes.filter(
    (type) => type.event_id === inventoryEventId,
  );
  const eventTickets = tickets.filter((ticket) =>
    eventTicketTypes.some((type) => type.id === ticket.ticket_type_id),
  );
  const eventSeats = seats.filter(
    (seat) => seat.venue_id === inventoryEvent?.venue_id,
  );

  function formFor(kind: EntityKind, record?: EntityRecord): FormConfig {
    const editing = Boolean(record);
    switch (kind) {
      case "venue": {
        const venue = record as Venue | undefined;
        return {
          title: editing ? "Edit venue" : "New venue",
          description: "The building that hosts events and owns its seats.",
          submitLabel: editing ? "Save venue" : "Create venue",
          fields: [
            {
              kind: "text",
              name: "name",
              label: "Name",
              placeholder: "The Grand Hall",
              defaultValue: venue?.name,
            },
            {
              kind: "select",
              name: "timezone",
              label: "Timezone",
              placeholder: "Choose a timezone",
              options: timezoneOptions(),
              defaultValue: venue?.timezone ?? localTimezone(),
            },
            {
              kind: "text",
              name: "address",
              label: "Address",
              placeholder: "100 Broadway, New York, NY",
              defaultValue: venue?.address,
            },
          ],
          submit: async (data) => {
            const body = {
              name: data.get("name"),
              timezone: data.get("timezone"),
              address: data.get("address"),
            };
            const saved = venue
              ? await api.patch<Venue>(`/venues/${venue.id}`, body)
              : await api.post<Venue>("/venues/", body);
            return `${editing ? "Updated" : "Created"} venue “${saved.name}”.`;
          },
        };
      }
      case "seat": {
        const seat = record as Seat | undefined;
        const venueId = seat?.venue_id ?? inventoryVenue?.id;
        return {
          title: editing ? "Edit seat" : "New seat",
          description: inventoryVenue
            ? `A seat at ${inventoryVenue.name}, reused across events.`
            : "Seats belong to a venue and are reused across events.",
          submitLabel: editing ? "Save seat" : "Create seat",
          fields: [
            {
              kind: "text",
              name: "section",
              label: "Section",
              placeholder: "Orchestra",
              defaultValue: seat?.section,
            },
            {
              kind: "text",
              name: "seat_row",
              label: "Row",
              placeholder: "A",
              defaultValue: seat?.seat_row,
            },
            {
              kind: "text",
              name: "seat_number",
              label: "Number",
              placeholder: "1",
              defaultValue: seat?.seat_number,
            },
          ],
          submit: async (data) => {
            if (venueId == null) {
              throw new Error("Open a venue’s seating screen before adding a seat.");
            }
            const body = {
              section: data.get("section"),
              seat_row: data.get("seat_row"),
              seat_number: data.get("seat_number"),
              venue_id: venueId,
            };
            const saved = seat
              ? await api.patch<Seat>(`/seats/${seat.id}`, body)
              : await api.post<Seat>("/seats/", body);
            return `${editing ? "Updated" : "Created"} seat ${seatLabel(saved)}.`;
          },
        };
      }
      case "event": {
        const event = record as Event | undefined;
        return {
          title: editing ? "Edit event" : "New event",
          description: "A dated performance at one of your venues.",
          submitLabel: editing ? "Save event" : "Create event",
          fields: [
            {
              kind: "text",
              name: "name",
              label: "Event name",
              placeholder: "Late Set at the Grand Hall",
              defaultValue: event?.name,
            },
            {
              kind: "select",
              name: "venue_id",
              label: "Venue",
              placeholder: "Choose a venue",
              options: venueOptions,
              defaultValue: event ? String(event.venue_id) : undefined,
            },
            {
              kind: "datetime",
              name: "starts_at",
              label: "Starts",
              defaultValue: toDatetimeLocal(event?.starts_at ?? nowUnix() + 86400),
            },
            {
              kind: "datetime",
              name: "ends_at",
              label: "Ends",
              defaultValue: toDatetimeLocal(
                event?.ends_at ?? nowUnix() + 86400 + 7200,
              ),
            },
          ],
          submit: async (data) => {
            const body = {
              name: data.get("name"),
              venue_id: Number(data.get("venue_id")),
              starts_at: fromDatetimeLocal(String(data.get("starts_at"))),
              ends_at: fromDatetimeLocal(String(data.get("ends_at"))),
            };
            const saved = event
              ? await api.patch<Event>(`/events/${event.id}`, body)
              : await api.post<Event>("/events/", body);
            return `${editing ? "Updated" : "Created"} event “${saved.name}”.`;
          },
        };
      }
      case "ticket-type": {
        const type = record as TicketType | undefined;
        const eventId = type?.event_id ?? inventoryEvent?.id;
        return {
          title: editing ? "Edit ticket type" : "New ticket type",
          description: inventoryEvent
            ? `A pricing tier for ${inventoryEvent.name}.`
            : "A pricing tier for one event, such as VIP or GA.",
          submitLabel: editing ? "Save ticket type" : "Create ticket type",
          fields: [
            {
              kind: "text",
              name: "tier",
              label: "Tier",
              placeholder: "VIP",
              defaultValue: type?.tier,
            },
          ],
          submit: async (data) => {
            if (eventId == null) {
              throw new Error("Open an event’s ticketing screen before adding a type.");
            }
            const body = {
              tier: data.get("tier"),
              event_id: eventId,
            };
            const saved = type
              ? await api.patch<TicketType>(`/ticket-types/${type.id}`, body)
              : await api.post<TicketType>("/ticket-types/", body);
            return `${editing ? "Updated" : "Created"} ${saved.tier} for ${eventName(saved.event_id)}.`;
          },
        };
      }
      case "ticket": {
        const ticket = record as Ticket | undefined;
        return {
          title: editing ? "Edit ticket" : "New ticket",
          description: inventoryEvent
            ? `Sell a seat at ${inventoryEvent.name}.`
            : "One sellable seat at a given tier and price.",
          submitLabel: editing ? "Save ticket" : "Create ticket",
          fields: [
            {
              kind: "select",
              name: "ticket_type_id",
              label: "Ticket type",
              placeholder: "Choose a ticket type",
              options: eventTicketTypes.map((item) => ({
                value: String(item.id),
                label: item.tier,
              })),
              defaultValue: ticket ? String(ticket.ticket_type_id) : undefined,
            },
            {
              kind: "select",
              name: "seat_id",
              label: "Seat",
              placeholder: "Choose a seat at this venue",
              options: eventSeats.map((seat) => ({
                value: String(seat.id),
                label: seatLabel(seat),
              })),
              defaultValue: ticket ? String(ticket.seat_id) : undefined,
            },
            {
              kind: "number",
              name: "price",
              label: "Price in dollars",
              placeholder: "45.00",
              min: "0",
              step: "0.01",
              defaultValue: ticket ? (ticket.price / 100).toFixed(2) : undefined,
            },
          ],
          submit: async (data) => {
            const body = {
              price: Math.round(Number(data.get("price")) * 100),
              seat_id: Number(data.get("seat_id")),
              ticket_type_id: Number(data.get("ticket_type_id")),
            };
            const saved = ticket
              ? await api.patch<Ticket>(`/tickets/${ticket.id}`, body)
              : await api.post<Ticket>("/tickets/", body);
            const seat = seats.find((item) => item.id === saved.seat_id);
            return `${editing ? "Updated" : "Created"} ${formatMoney(saved.price)} ticket for ${
              seat ? seatLabel(seat) : `seat #${saved.seat_id}`
            }.`;
          },
        };
      }
      case "user": {
        const user = record as User | undefined;
        return {
          title: editing ? "Edit buyer" : "New buyer",
          description: "Buyers are attached to orders at checkout.",
          submitLabel: editing ? "Save buyer" : "Create buyer",
          fields: [
            {
              kind: "text",
              name: "name",
              label: "Name",
              placeholder: "Alex Rivera",
              defaultValue: user?.name,
            },
            {
              kind: "email",
              name: "email",
              label: "Email",
              placeholder: "alex@example.com",
              defaultValue: user?.email,
            },
          ],
          submit: async (data) => {
            const body = { name: data.get("name"), email: data.get("email") };
            const saved = user
              ? await api.patch<User>(`/users/${user.id}`, body)
              : await api.post<User>("/users/", body);
            return `${editing ? "Updated" : "Created"} buyer ${saved.name}.`;
          },
        };
      }
      case "tax-rate": {
        const rate = record as TaxRate | undefined;
        return {
          title: editing ? "Edit tax rate" : "New tax rate",
          description: "Applied to the subtotal when an order is placed.",
          submitLabel: editing ? "Save tax rate" : "Create tax rate",
          fields: [
            {
              kind: "text",
              name: "jurisdiction",
              label: "Jurisdiction",
              placeholder: "NY",
              defaultValue: rate?.jurisdiction,
            },
            {
              kind: "text",
              name: "tax_type",
              label: "Tax type",
              placeholder: "sales",
              defaultValue: rate?.tax_type,
            },
            {
              kind: "number",
              name: "percent",
              label: "Percent",
              placeholder: "8.875",
              min: "0",
              step: "0.001",
              defaultValue: rate ? String(rate.rate * 100) : undefined,
            },
            {
              kind: "datetime",
              name: "effective_from",
              label: "Effective from",
              defaultValue: toDatetimeLocal(rate?.effective_from ?? nowUnix()),
            },
          ],
          submit: async (data) => {
            const body = {
              jurisdiction: data.get("jurisdiction"),
              tax_type: data.get("tax_type"),
              rate: Number(data.get("percent")) / 100,
              effective_from: fromDatetimeLocal(String(data.get("effective_from"))),
            };
            const saved = rate
              ? await api.patch<TaxRate>(`/tax-rates/${rate.id}`, body)
              : await api.post<TaxRate>("/tax-rates/", body);
            return `${editing ? "Updated" : "Created"} ${saved.jurisdiction} ${saved.tax_type} rate at ${(
              saved.rate * 100
            ).toFixed(3)}%.`;
          },
        };
      }
    }
  }

  function openCreate(kind: EntityKind) {
    setMessage(null);
    setError(null);
    setDialog({ action: "create", kind });
  }

  function openEdit(kind: EntityKind, record: EntityRecord) {
    setMessage(null);
    setError(null);
    setDialog({ action: "edit", kind, record });
  }

  function openDelete(kind: EntityKind, id: number, label: string) {
    setMessage(null);
    setError(null);
    setDialog({ action: "delete", kind, id, label });
  }

  async function handleSave(config: FormConfig, data: FormData) {
    const summary = await config.submit(data);
    await refresh();
    setDialog(null);
    setMessage(summary);
  }

  async function handleDelete(kind: EntityKind, id: number, label: string) {
    await api.delete(DELETE_PATH[kind](id));
    await refresh();
    setDialog(null);
    setMessage(`Deleted ${label}.`);
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

  const form =
    dialog && dialog.action !== "delete"
      ? formFor(dialog.kind, dialog.action === "edit" ? dialog.record : undefined)
      : null;

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
            ["people", "Buyers"],
            ["tax", "Tax"],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            className={tab === id ? "tab active" : "tab"}
            onClick={() => {
              setTab(id);
              setInventoryVenueId(null);
              setInventoryEventId(null);
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "house" && inventoryVenue && (
        <section>
          <div className="panel event-inventory-head">
            <button
              type="button"
              className="ghost compact"
              onClick={() => setInventoryVenueId(null)}
            >
              ← All venues
            </button>
            <div>
              <p className="eyebrow">Seating</p>
              <h2>{inventoryVenue.name}</h2>
              <p className="hint">
                {inventoryVenue.address} · {inventoryVenue.timezone}
              </p>
            </div>
          </div>
          <Collection
            title="Seats"
            count={venueSeats.length}
            actionLabel="New seat"
            onNew={() => openCreate("seat")}
            empty="No seats yet. Seats are what tickets are sold against."
          >
            {venueSeats.map((seat) => (
              <li key={seat.id}>
                <div>
                  <strong>{seatLabel(seat)}</strong>
                </div>
                <RowActions
                  onEdit={() => openEdit("seat", seat)}
                  onDelete={() =>
                    openDelete("seat", seat.id, `seat ${seatLabel(seat)}`)
                  }
                />
              </li>
            ))}
          </Collection>
        </section>
      )}

      {tab === "house" && !inventoryVenue && (
        <Collection
          title="Venues"
          count={venues.length}
          actionLabel="New venue"
          onNew={() => openCreate("venue")}
          empty="No venues yet. Create one to start building the house."
        >
          {venues.map((venue) => {
            const seatCount = seats.filter(
              (seat) => seat.venue_id === venue.id,
            ).length;
            return (
              <li key={venue.id}>
                <div>
                  <strong>{venue.name}</strong>
                  <span>
                    {venue.address} · {venue.timezone} · {seatCount} seats
                  </span>
                </div>
                <RowActions
                  extra={
                    <button
                      type="button"
                      className="ghost compact"
                      onClick={() => {
                        setMessage(null);
                        setError(null);
                        setInventoryVenueId(venue.id);
                      }}
                    >
                      Seats
                    </button>
                  }
                  onEdit={() => openEdit("venue", venue)}
                  onDelete={() =>
                    openDelete("venue", venue.id, `venue “${venue.name}”`)
                  }
                />
              </li>
            );
          })}
        </Collection>
      )}

      {tab === "events" && inventoryEvent && (
        <section>
          <div className="panel event-inventory-head">
            <button
              type="button"
              className="ghost compact"
              onClick={() => setInventoryEventId(null)}
            >
              ← All events
            </button>
            <div>
              <p className="eyebrow">Ticketing</p>
              <h2>{inventoryEvent.name}</h2>
              <p className="hint">
                {venueName(inventoryEvent.venue_id)} · {formatWhen(inventoryEvent.starts_at)}
              </p>
            </div>
          </div>
          <div className="split">
            <Collection
              title="Ticket types"
              count={eventTicketTypes.length}
              actionLabel="New ticket type"
              onNew={() => openCreate("ticket-type")}
              empty="No tiers yet. Add GA, VIP, or another type before selling seats."
            >
              {eventTicketTypes.map((type) => (
                <li key={type.id}>
                  <div>
                    <strong>{type.tier}</strong>
                    <span>
                      {
                        eventTickets.filter(
                          (ticket) => ticket.ticket_type_id === type.id,
                        ).length
                      }{" "}
                      tickets
                    </span>
                  </div>
                  <RowActions
                    onEdit={() => openEdit("ticket-type", type)}
                    onDelete={() =>
                      openDelete("ticket-type", type.id, `${type.tier} for ${inventoryEvent.name}`)
                    }
                  />
                </li>
              ))}
            </Collection>
            <Collection
              title="Tickets"
              count={eventTickets.length}
              actionLabel="New ticket"
              onNew={() => openCreate("ticket")}
              empty={
                eventTicketTypes.length === 0
                  ? "Add a ticket type first, then create seats for this event."
                  : eventSeats.length === 0
                    ? "This venue has no seats yet. Open the venue under Venues & seats and add them there."
                    : "No tickets yet for this event."
              }
            >
              {eventTickets.map((ticket) => {
                const seat = seats.find((item) => item.id === ticket.seat_id);
                const type = ticketTypes.find(
                  (item) => item.id === ticket.ticket_type_id,
                );
                const label = seat ? seatLabel(seat) : `seat #${ticket.seat_id}`;
                return (
                  <li key={ticket.id}>
                    <div>
                      <strong>{label}</strong>
                      <span>
                        {type?.tier ?? `Type #${ticket.ticket_type_id}`} ·{" "}
                        {formatMoney(ticket.price)}
                      </span>
                    </div>
                    <div className="row-meta">
                      <em className={ticket.sold_at ? "sold" : "available"}>
                        {ticket.sold_at ? "Sold" : "Available"}
                      </em>
                      <RowActions
                        onEdit={() => openEdit("ticket", ticket)}
                        onDelete={() =>
                          openDelete("ticket", ticket.id, `ticket for ${label}`)
                        }
                      />
                    </div>
                  </li>
                );
              })}
            </Collection>
          </div>
        </section>
      )}

      {tab === "events" && !inventoryEvent && (
        <Collection
          title="Events"
          count={events.length}
          actionLabel="New event"
          onNew={() => openCreate("event")}
          empty="No events yet. Attendees only see events that exist here."
        >
          {events.map((event) => {
            const ticketCount = tickets.filter((ticket) =>
              ticketTypes.some(
                (type) =>
                  type.id === ticket.ticket_type_id && type.event_id === event.id,
              ),
            ).length;
            return (
              <li key={event.id}>
                <div>
                  <strong>{event.name}</strong>
                  <span>
                    {venueName(event.venue_id)} · {formatWhen(event.starts_at)} ·{" "}
                    {ticketCount} tickets
                  </span>
                </div>
                <RowActions
                  extra={
                    <button
                      type="button"
                      className="ghost compact"
                      onClick={() => {
                        setMessage(null);
                        setError(null);
                        setInventoryEventId(event.id);
                      }}
                    >
                      Tickets
                    </button>
                  }
                  onEdit={() => openEdit("event", event)}
                  onDelete={() => openDelete("event", event.id, `event “${event.name}”`)}
                />
              </li>
            );
          })}
        </Collection>
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
              <RowActions
                onEdit={() => openEdit("user", user)}
                onDelete={() => openDelete("user", user.id, `buyer ${user.name}`)}
              />
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
              <div className="row-meta">
                <em>{(rate.rate * 100).toFixed(3)}%</em>
                <RowActions
                  onEdit={() => openEdit("tax-rate", rate)}
                  onDelete={() =>
                    openDelete(
                      "tax-rate",
                      rate.id,
                      `${rate.jurisdiction} ${rate.tax_type} rate`,
                    )
                  }
                />
              </div>
            </li>
          ))}
        </Collection>
      )}

      {form && dialog && dialog.action !== "delete" && (
        <FormModal
          key={`${dialog.action}-${dialog.kind}-${dialog.action === "edit" ? dialog.record.id : "new"}`}
          title={form.title}
          description={form.description}
          fields={form.fields}
          submitLabel={form.submitLabel}
          onSubmit={(data) => handleSave(form, data)}
          onClose={() => setDialog(null)}
        />
      )}
      {dialog?.action === "delete" && (
        <ConfirmModal
          title="Delete this record?"
          body={`This cannot be undone. ${dialog.label} will be removed if nothing else depends on it.`}
          confirmLabel="Delete"
          onConfirm={() => handleDelete(dialog.kind, dialog.id, dialog.label)}
          onClose={() => setDialog(null)}
        />
      )}
    </section>
  );
}

function RowActions({
  extra,
  onEdit,
  onDelete,
}: {
  extra?: ReactNode;
  onEdit: () => void;
  onDelete: () => void;
}) {
  return (
    <div className="row-actions">
      {extra}
      <button type="button" className="ghost compact" onClick={onEdit}>
        Edit
      </button>
      <button type="button" className="danger-ghost compact" onClick={onDelete}>
        Delete
      </button>
    </div>
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
