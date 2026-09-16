export type User = {
  id: number;
  name: string;
  email: string;
  created_at: number;
  updated_at: number;
};

export type Venue = {
  id: number;
  name: string;
  timezone: string;
  address: string;
  created_at: number;
  updated_at: number;
};

export type Event = {
  id: number;
  name: string;
  venue_id: number;
  starts_at: number;
  ends_at: number;
  created_at: number;
  updated_at: number;
};

export type Seat = {
  id: number;
  section: string;
  seat_row: string;
  seat_number: string;
  venue_id: number;
  created_at: number;
  updated_at: number;
};

export type TicketType = {
  id: number;
  tier: string;
  event_id: number;
  created_at: number;
  updated_at: number;
};

export type Ticket = {
  id: number;
  price: number;
  held_until: number | null;
  sold_at: number | null;
  seat_id: number;
  event_id: number;
  ticket_type_id: number;
  created_at: number;
  updated_at: number;
};

export type Order = {
  id: number;
  status: string;
  user_id: number;
  subtotal: number;
  tax_amount: number;
  total_charged: number;
  tax_rate_applied: number;
  tax_jurisdiction: string;
  created_at: number;
  updated_at: number;
};

export type OrderItem = {
  order_id: number;
  ticket_id: number;
  created_at: number;
  updated_at: number;
};

export type TaxRate = {
  id: number;
  jurisdiction: string;
  tax_type: string;
  rate: number;
  effective_from: number;
  effective_to: number | null;
  created_at: number;
  updated_at: number;
};
