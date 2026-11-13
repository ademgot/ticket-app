import type { FormEvent } from "react";

export type DatePreset = "all" | "today" | "weekend" | "week" | "month";

export type EventSearchValues = {
  location: string;
  dates: DatePreset;
  q: string;
};

export const EMPTY_EVENT_SEARCH: EventSearchValues = {
  location: "",
  dates: "all",
  q: "",
};

function startOfDay(date: Date): Date {
  const next = new Date(date);
  next.setHours(0, 0, 0, 0);
  return next;
}

function addDays(date: Date, days: number): Date {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

export function dateBounds(preset: DatePreset): {
  starts_after?: string;
  starts_before?: string;
} {
  const today = startOfDay(new Date());
  if (preset === "today") {
    return {
      starts_after: today.toISOString(),
      starts_before: addDays(today, 1).toISOString(),
    };
  }
  if (preset === "weekend") {
    const day = today.getDay();
    const saturday = addDays(today, day === 0 ? -1 : 6 - day);
    return {
      starts_after: saturday.toISOString(),
      starts_before: addDays(saturday, 2).toISOString(),
    };
  }
  if (preset === "week") {
    return {
      starts_after: today.toISOString(),
      starts_before: addDays(today, 7).toISOString(),
    };
  }
  if (preset === "month") {
    const start = new Date(today.getFullYear(), today.getMonth(), 1);
    const end = new Date(today.getFullYear(), today.getMonth() + 1, 1);
    return { starts_after: start.toISOString(), starts_before: end.toISOString() };
  }
  return {};
}

export function EventSearch({
  values,
  onChange,
  onSearch,
}: {
  values: EventSearchValues;
  onChange: (values: EventSearchValues) => void;
  onSearch: () => void;
}) {
  function submit(event: FormEvent) {
    event.preventDefault();
    onSearch();
  }

  return (
    <form className="event-search" onSubmit={submit}>
      <div className="event-search__bar">
        <label className="event-search__field">
          <PinIcon />
          <span className="event-search__copy">
            <span className="event-search__label">Location</span>
            <input
              value={values.location}
              placeholder="City or postal code"
              onChange={(event) =>
                onChange({ ...values, location: event.target.value })
              }
            />
          </span>
        </label>
        <label className="event-search__field">
          <CalendarIcon />
          <span className="event-search__copy">
            <span className="event-search__label">Dates</span>
            <select
              value={values.dates}
              onChange={(event) =>
                onChange({ ...values, dates: event.target.value as DatePreset })
              }
            >
              <option value="all">All dates</option>
              <option value="today">Today</option>
              <option value="weekend">This weekend</option>
              <option value="week">Next 7 days</option>
              <option value="month">This month</option>
            </select>
          </span>
        </label>
        <label className="event-search__field event-search__field--query">
          <SearchIcon />
          <span className="event-search__copy">
            <span className="event-search__label">Search</span>
            <input
              value={values.q}
              placeholder="Event or venue"
              onChange={(event) => onChange({ ...values, q: event.target.value })}
            />
          </span>
        </label>
      </div>
      <button type="submit" className="primary event-search__submit">
        Search
      </button>
    </form>
  );
}

function PinIcon() {
  return (
    <svg className="event-search__icon" viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="currentColor"
        d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7zm0 9.5a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z"
      />
    </svg>
  );
}

function CalendarIcon() {
  return (
    <svg className="event-search__icon" viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="currentColor"
        d="M7 2h2v2h6V2h2v2h3v18H4V4h3V2zm11 8H6v10h12V10z"
      />
    </svg>
  );
}

function SearchIcon() {
  return (
    <svg className="event-search__icon" viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="currentColor"
        d="M15.5 14h-.79l-.28-.27A6.47 6.47 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79L20 21.49 21.49 20 15.5 14zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"
      />
    </svg>
  );
}
