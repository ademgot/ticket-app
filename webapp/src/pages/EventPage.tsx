import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import type {
  Event,
  OrderItem,
  Seat,
  Ticket,
  TicketType,
  Venue,
} from "../api/types";
import { useCart } from "../cart";
import { formatMoney, formatWhen, seatLabel } from "../lib/format";

export function EventPage() {
  const { eventId } = useParams();
  const { add, has, remove } = useCart();
  const [event, setEvent] = useState<Event | null>(null);
  const [venue, setVenue] = useState<Venue | null>(null);
  const [ticketTypes, setTicketTypes] = useState<TicketType[]>([]);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [seats, setSeats] = useState<Seat[]>([]);
  const [claimedIds, setClaimedIds] = useState<Set<number>>(new Set());
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!eventId) return;
    Promise.all([
      api.get<Event>(`/events/${eventId}`),
      api.get<Venue[]>("/venues/"),
      api.get<TicketType[]>("/ticket-types/"),
      api.get<Ticket[]>("/tickets/"),
      api.get<Seat[]>("/seats/"),
      api.get<OrderItem[]>("/order-items/"),
    ])
      .then(([loadedEvent, venues, types, ticketList, seatList, items]) => {
        setEvent(loadedEvent);
        setVenue(venues.find((item) => item.id === loadedEvent.venue_id) ?? null);
        setTicketTypes(types.filter((type) => type.event_id === loadedEvent.id));
        setTickets(ticketList.filter((ticket) => ticket.event_id === loadedEvent.id));
        setSeats(seatList);
        setClaimedIds(new Set(items.map((item) => item.ticket_id)));
      })
      .catch((err: Error) => setError(err.message));
  }, [eventId]);

  const inventory = tickets;

  if (error) {
    return <p className="banner error">{error}</p>;
  }
  if (!event) {
    return <p className="banner">Loading event…</p>;
  }

  return (
    <section>
      <div className="page-head">
        <p className="eyebrow">{venue?.name ?? "Unknown venue"}</p>
        <h1>{event.name}</h1>
        <p>
          {formatWhen(event.starts_at)} — {formatWhen(event.ends_at)}
          {venue ? ` · ${venue.address}` : ""}
        </p>
      </div>
      {ticketTypes.length === 0 && (
        <p className="banner">
          This event has no ticket types yet. Add them under Manage.
        </p>
      )}
      {ticketTypes.map((type) => {
        const typeTickets = inventory.filter(
          (ticket) => ticket.ticket_type_id === type.id,
        );
        return (
          <article key={type.id} className="panel">
            <header className="panel-head">
              <h2>{type.tier}</h2>
              <span>{typeTickets.length} seats in inventory</span>
            </header>
            <ul className="seat-list">
              {typeTickets.map((ticket) => {
                const seat = seats.find((item) => item.id === ticket.seat_id);
                const taken = Boolean(ticket.sold_at) || claimedIds.has(ticket.id);
                const inCart = has(ticket.id);
                return (
                  <li key={ticket.id}>
                    <div>
                      <strong>{seat ? seatLabel(seat) : `Seat #${ticket.seat_id}`}</strong>
                      <span>{formatMoney(ticket.price)}</span>
                    </div>
                    {taken ? (
                      <em className="sold">Sold</em>
                    ) : (
                      <button
                        type="button"
                        className={inCart ? "ghost" : "primary"}
                        onClick={() => (inCart ? remove(ticket.id) : add(ticket))}
                      >
                        {inCart ? "Remove" : "Hold seat"}
                      </button>
                    )}
                  </li>
                );
              })}
            </ul>
          </article>
        );
      })}
      <p className="footer-link">
        Ready? <Link to="/user/checkout">Go to checkout</Link>
      </p>
    </section>
  );
}
