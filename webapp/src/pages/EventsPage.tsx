import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { pageUrl } from "../api/paging";
import type { Event, Page } from "../api/types";
import {
  dateBounds,
  EMPTY_EVENT_SEARCH,
  EventSearch,
  type EventSearchValues,
} from "../components/EventSearch";
import { Pager } from "../components/Pager";
import { formatWhen } from "../lib/format";

export function EventsPage() {
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [events, setEvents] = useState<Event[]>([]);
  const [draft, setDraft] = useState<EventSearchValues>(EMPTY_EVENT_SEARCH);
  const [applied, setApplied] = useState<EventSearchValues>(EMPTY_EVENT_SEARCH);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const bounds = dateBounds(applied.dates);
    api
      .get<Page<Event>>(
        pageUrl("/events/", page, {
          q: applied.q.trim(),
          location: applied.location.trim(),
          starts_after: bounds.starts_after,
          starts_before: bounds.starts_before,
        }),
      )
      .then((eventPage) => {
        setEvents(eventPage.items);
        setTotal(eventPage.total);
        setError(null);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoaded(true));
  }, [page, applied]);

  function search() {
    setPage(1);
    setApplied({ ...draft });
  }

  const filtering =
    applied.q.trim() !== "" ||
    applied.location.trim() !== "" ||
    applied.dates !== "all";

  return (
    <section>
      <div className="page-head">
        <h1>What’s on</h1>
        <p>Pick a night, then grab seats from live inventory.</p>
      </div>
      <EventSearch values={draft} onChange={setDraft} onSearch={search} />
      {error && <p className="banner error">{error}</p>}
      {loaded && !error && total === 0 && (
        <p className="banner">
          {filtering
            ? "No events match that search."
            : "No events are on sale yet. Ask an organizer to create an event and add ticket inventory."}
        </p>
      )}
      <Pager page={page} total={total} onPage={setPage} />
      <div className="event-grid">
        {events.map((event) => (
          <Link key={event.id} className="event-card" to={`/user/events/${event.id}`}>
            <p className="eyebrow">
              {event.venue_name ?? `Venue #${event.venue_id}`}
            </p>
            <h2>{event.name}</h2>
            <p>
              {formatWhen(event.starts_at)}
              <span> → </span>
              {formatWhen(event.ends_at)}
            </p>
          </Link>
        ))}
      </div>
      <Pager page={page} total={total} onPage={setPage} />
    </section>
  );
}
