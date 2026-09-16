import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type {
  Order,
  OrderItem,
  Seat,
  TaxRate,
  Ticket,
  TicketType,
  User,
} from "../api/types";
import { FormModal } from "../components/FormModal";
import { useCart } from "../cart";
import { formatMoney, nowUnix, seatLabel } from "../lib/format";

export function CheckoutPage() {
  const { ticketIds, remove, clear } = useCart();
  const navigate = useNavigate();
  const [users, setUsers] = useState<User[]>([]);
  const [taxRates, setTaxRates] = useState<TaxRate[]>([]);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [seats, setSeats] = useState<Seat[]>([]);
  const [ticketTypes, setTicketTypes] = useState<TicketType[]>([]);
  const [claimedIds, setClaimedIds] = useState<Set<number>>(new Set());
  const [userId, setUserId] = useState("");
  const [taxRateId, setTaxRateId] = useState("");
  const [addingBuyer, setAddingBuyer] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get<User[]>("/users/"),
      api.get<TaxRate[]>("/tax-rates/"),
      api.get<Ticket[]>("/tickets/"),
      api.get<Seat[]>("/seats/"),
      api.get<TicketType[]>("/ticket-types/"),
      api.get<OrderItem[]>("/order-items/"),
    ])
      .then(([userList, rates, ticketList, seatList, types, items]) => {
        setUsers(userList);
        setTaxRates(rates);
        setTickets(ticketList);
        setSeats(seatList);
        setTicketTypes(types);
        setClaimedIds(new Set(items.map((item) => item.ticket_id)));
        if (userList[0]) setUserId(String(userList[0].id));
        if (rates[0]) setTaxRateId(String(rates[0].id));
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  const selected = useMemo(
    () => tickets.filter((ticket) => ticketIds.includes(ticket.id)),
    [tickets, ticketIds],
  );
  const subtotal = selected.reduce((sum, ticket) => sum + ticket.price, 0);
  const taxRate = taxRates.find((rate) => String(rate.id) === taxRateId);
  const taxAmount = taxRate ? Math.round(subtotal * taxRate.rate) : 0;
  const total = subtotal + taxAmount;

  async function createBuyer(data: FormData) {
    const user = await api.post<User>("/users/", {
      name: data.get("name"),
      email: data.get("email"),
    });
    setUsers((current) => [...current, user]);
    setUserId(String(user.id));
    setAddingBuyer(false);
    setMessage(`Added buyer ${user.name} and selected them for this order.`);
  }

  async function placeOrder() {
    setError(null);
    setMessage(null);
    if (!userId) {
      setError("Choose or create a buyer first.");
      return;
    }
    if (!taxRate) {
      setError("Choose a tax rate. Add one under Manage if the list is empty.");
      return;
    }
    if (selected.length === 0) {
      setError("Your cart is empty.");
      return;
    }
    const blocked = selected.find(
      (ticket) => ticket.sold_at || claimedIds.has(ticket.id),
    );
    if (blocked) {
      setError(`Ticket #${blocked.id} is no longer available.`);
      return;
    }

    setBusy(true);
    try {
      const order = await api.post<Order>("/orders/", {
        status: "paid",
        user_id: Number(userId),
        subtotal,
        tax_amount: taxAmount,
        total_charged: total,
        tax_rate_applied: taxRate.rate,
        tax_jurisdiction: taxRate.jurisdiction,
      });
      const soldAt = nowUnix();
      for (const ticket of selected) {
        await api.post("/order-items/", {
          order_id: order.id,
          ticket_id: ticket.id,
        });
        await api.patch(`/tickets/${ticket.id}`, { sold_at: soldAt });
      }
      clear();
      navigate(`/user/orders/${order.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Checkout failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="split">
      <div>
        <div className="page-head">
          <h1>Checkout</h1>
          <p>Seats stay in your cart until you pay or someone else claims them.</p>
        </div>
        {message && <p className="banner success">{message}</p>}
        {error && <p className="banner error">{error}</p>}
        {selected.length === 0 ? (
          <p className="banner">
            Nothing held. <Link to="/user">Browse events</Link>
          </p>
        ) : (
          <ul className="seat-list">
            {selected.map((ticket) => {
              const seat = seats.find((item) => item.id === ticket.seat_id);
              const type = ticketTypes.find(
                (item) => item.id === ticket.ticket_type_id,
              );
              return (
                <li key={ticket.id}>
                  <div>
                    <strong>{seat ? seatLabel(seat) : `Ticket #${ticket.id}`}</strong>
                    <span>
                      {type?.tier ?? "Ticket"} · {formatMoney(ticket.price)}
                    </span>
                  </div>
                  <button type="button" className="ghost" onClick={() => remove(ticket.id)}>
                    Remove
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>
      <aside className="panel sticky">
        <h2>Buyer & tax</h2>
        <label>
          Buyer
          <select value={userId} onChange={(event) => setUserId(event.target.value)}>
            <option value="">Select a buyer</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name} ({user.email})
              </option>
            ))}
          </select>
        </label>
        <button type="button" className="ghost" onClick={() => setAddingBuyer(true)}>
          New buyer
        </button>
        <label>
          Tax rate
          <select
            value={taxRateId}
            onChange={(event) => setTaxRateId(event.target.value)}
          >
            <option value="">Select a rate</option>
            {taxRates.map((rate) => (
              <option key={rate.id} value={rate.id}>
                {rate.jurisdiction} {rate.tax_type} ({(rate.rate * 100).toFixed(2)}%)
              </option>
            ))}
          </select>
        </label>
        <dl className="totals">
          <div>
            <dt>Subtotal</dt>
            <dd>{formatMoney(subtotal)}</dd>
          </div>
          <div>
            <dt>Tax</dt>
            <dd>{formatMoney(taxAmount)}</dd>
          </div>
          <div>
            <dt>Due</dt>
            <dd>{formatMoney(total)}</dd>
          </div>
        </dl>
        <button
          type="button"
          className="primary wide"
          disabled={busy || selected.length === 0}
          onClick={() => void placeOrder()}
        >
          {busy ? "Charging…" : "Place order"}
        </button>
      </aside>
      {addingBuyer && (
        <FormModal
          title="New buyer"
          description="The buyer this order is charged to."
          submitLabel="Create buyer"
          fields={[
            { kind: "text", name: "name", label: "Name", placeholder: "Alex Rivera" },
            {
              kind: "email",
              name: "email",
              label: "Email",
              placeholder: "alex@example.com",
            },
          ]}
          onSubmit={createBuyer}
          onClose={() => setAddingBuyer(false)}
        />
      )}
    </section>
  );
}
