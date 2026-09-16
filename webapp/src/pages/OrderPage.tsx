import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import type {
  Order,
  OrderItem,
  Seat,
  Ticket,
  TicketType,
  User,
} from "../api/types";
import { formatMoney, formatWhen, seatLabel } from "../lib/format";

export function OrderPage() {
  const { orderId } = useParams();
  const [order, setOrder] = useState<Order | null>(null);
  const [buyer, setBuyer] = useState<User | null>(null);
  const [items, setItems] = useState<OrderItem[]>([]);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [seats, setSeats] = useState<Seat[]>([]);
  const [types, setTypes] = useState<TicketType[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!orderId) return;
    Promise.all([
      api.get<Order>(`/orders/${orderId}`),
      api.get<OrderItem[]>("/order-items/"),
      api.get<Ticket[]>("/tickets/"),
      api.get<Seat[]>("/seats/"),
      api.get<TicketType[]>("/ticket-types/"),
      api.get<User[]>("/users/"),
    ])
      .then(([loaded, allItems, ticketList, seatList, typeList, users]) => {
        setOrder(loaded);
        setItems(allItems.filter((item) => item.order_id === loaded.id));
        setTickets(ticketList);
        setSeats(seatList);
        setTypes(typeList);
        setBuyer(users.find((user) => user.id === loaded.user_id) ?? null);
      })
      .catch((err: Error) => setError(err.message));
  }, [orderId]);

  if (error) return <p className="banner error">{error}</p>;
  if (!order) return <p className="banner">Loading order…</p>;

  return (
    <section>
      <div className="page-head">
        <p className="eyebrow">Order #{order.id}</p>
        <h1>{buyer ? buyer.name : `User #${order.user_id}`}</h1>
        <p>
          {order.status} · {formatWhen(order.created_at)} · {order.tax_jurisdiction}{" "}
          tax {(order.tax_rate_applied * 100).toFixed(2)}%
        </p>
      </div>
      <ul className="seat-list">
        {items.map((item) => {
          const ticket = tickets.find((entry) => entry.id === item.ticket_id);
          const seat = seats.find((entry) => entry.id === ticket?.seat_id);
          const type = types.find((entry) => entry.id === ticket?.ticket_type_id);
          return (
            <li key={`${item.order_id}-${item.ticket_id}`}>
              <div>
                <strong>
                  {seat ? seatLabel(seat) : `Ticket #${item.ticket_id}`}
                </strong>
                <span>
                  {type?.tier ?? "Ticket"}
                  {ticket ? ` · ${formatMoney(ticket.price)}` : ""}
                </span>
              </div>
            </li>
          );
        })}
      </ul>
      <dl className="totals panel">
        <div>
          <dt>Subtotal</dt>
          <dd>{formatMoney(order.subtotal)}</dd>
        </div>
        <div>
          <dt>Tax</dt>
          <dd>{formatMoney(order.tax_amount)}</dd>
        </div>
        <div>
          <dt>Charged</dt>
          <dd>{formatMoney(order.total_charged)}</dd>
        </div>
      </dl>
    </section>
  );
}
