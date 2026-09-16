import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { Event, Venue } from "../api/types";
import { formatWhen } from "../lib/format";

export function EventsPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [venues, setVenues] = useState<Venue[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.get<Event[]>("/events/"), api.get<Venue[]>("/venues/")])
      .then(([eventList, venueList]) => {
        setEvents(eventList);
        setVenues(venueList);
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  const venueName = (venueId: number) =>
    venues.find((venue) => venue.id === venueId)?.name ?? `Venue #${venueId}`;

  return (
    <section>
      <div className="page-head">
        <h1>What’s on</h1>
        <p>Pick a night, then grab seats from live inventory.</p>
      </div>
      {error && <p className="banner error">{error}</p>}
      {!error && events.length === 0 && (
        <p className="banner">
          No events are on sale yet. Ask an organizer to create an event and
          add ticket inventory.
        </p>
      )}
      <div className="event-grid">
        {events.map((event) => (
          <Link key={event.id} className="event-card" to={`/user/events/${event.id}`}>
            <p className="eyebrow">{venueName(event.venue_id)}</p>
            <h2>{event.name}</h2>
            <p>
              {formatWhen(event.starts_at)}
              <span> → </span>
              {formatWhen(event.ends_at)}
            </p>
          </Link>
        ))}
      </div>
    </section>
  );
}
