export function formatMoney(cents: number): string {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: "USD",
  }).format(cents / 100);
}

export function formatWhen(value: string | number): string {
  const date =
    typeof value === "number" ? new Date(value * 1000) : new Date(value);
  return date.toLocaleString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function toDate(value: string | number | Date): Date {
  if (value instanceof Date) return value;
  if (typeof value === "number") return new Date(value * 1000);
  return new Date(value);
}

export function toDatetimeLocal(value: string | number | Date): string {
  const date = toDate(value);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

/** Convert a datetime-local input value to an ISO-8601 string for the API. */
export function fromDatetimeLocal(value: string): string {
  return new Date(value).toISOString();
}

export function nowIso(): string {
  return new Date().toISOString();
}

export function hoursFromNowIso(hours: number): string {
  return new Date(Date.now() + hours * 3600 * 1000).toISOString();
}

export function seatLabel(seat: {
  section: string;
  seat_row: string;
  seat_number: string;
}): string {
  return `${seat.section} · Row ${seat.seat_row} · Seat ${seat.seat_number}`;
}

const FALLBACK_TIMEZONES = [
  "UTC",
  "America/New_York",
  "America/Chicago",
  "America/Denver",
  "America/Los_Angeles",
  "America/Toronto",
  "Europe/London",
  "Europe/Paris",
  "Asia/Tokyo",
];

export function ianaTimezones(): string[] {
  const supported = Intl.supportedValuesOf?.("timeZone");
  return supported?.length ? [...supported] : FALLBACK_TIMEZONES;
}

export function localTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

export function timezoneOptions(): { value: string; label: string }[] {
  const now = new Date();
  return ianaTimezones().map((zone) => {
    const offset = new Intl.DateTimeFormat(undefined, {
      timeZone: zone,
      timeZoneName: "shortOffset",
    })
      .formatToParts(now)
      .find((part) => part.type === "timeZoneName")?.value;
    const name = zone.replaceAll("_", " ");
    return {
      value: zone,
      label: offset ? `${name} (${offset})` : name,
    };
  });
}
