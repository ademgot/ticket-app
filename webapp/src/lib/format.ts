export function formatMoney(cents: number): string {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: "USD",
  }).format(cents / 100);
}

export function formatWhen(unixSeconds: number): string {
  return new Date(unixSeconds * 1000).toLocaleString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function toDatetimeLocal(unixSeconds: number): string {
  const date = new Date(unixSeconds * 1000);
  const pad = (value: number) => String(value).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function fromDatetimeLocal(value: string): number {
  return Math.floor(new Date(value).getTime() / 1000);
}

export function nowUnix(): number {
  return Math.floor(Date.now() / 1000);
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
