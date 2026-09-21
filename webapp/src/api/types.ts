export type User = {
  id: number;
  name: string;
  email: string;
  created_at: string;
  updated_at: string;
};

export type Venue = {
  id: number;
  name: string;
  timezone: string;
  address: string;
  created_at: string;
  updated_at: string;
};

export type Event = {
  id: number;
  name: string;
  venue_id: number;
  starts_at: string;
  ends_at: string;
  created_at: string;
  updated_at: string;
};

export type Seat = {
  id: number;
  section: string;
  seat_row: string;
  seat_number: string;
  venue_id: number;
  created_at: string;
  updated_at: string;
};

export type TicketType = {
  id: number;
  tier: string;
  event_id: number;
  created_at: string;
  updated_at: string;
};

export type Ticket = {
  id: number;
  price: number;
  held_until: string | null;
  sold_at: string | null;
  held_by_user_id: number | null;
  sold_to_user_id: number | null;
  seat_id: number;
  event_id: number;
  ticket_type_id: number;
  created_at: string;
  updated_at: string;
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
  created_at: string;
  updated_at: string;
};

export type OrderItem = {
  order_id: number;
  ticket_id: number;
  created_at: string;
  updated_at: string;
};

export type TaxRate = {
  id: number;
  jurisdiction: string;
  tax_type: string;
  rate: number;
  effective_from: string;
  effective_to: string | null;
  created_at: string;
  updated_at: string;
};
