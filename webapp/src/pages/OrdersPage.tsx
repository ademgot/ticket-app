import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { Order, User } from "../api/types";
import { formatMoney, formatWhen } from "../lib/format";

export function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.get<Order[]>("/orders/"), api.get<User[]>("/users/")])
      .then(([orderList, userList]) => {
        setOrders(orderList);
        setUsers(userList);
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  const buyer = (userId: number) =>
    users.find((user) => user.id === userId)?.name ?? `User #${userId}`;

  return (
    <section>
      <div className="page-head">
        <h1>Orders</h1>
        <p>Every paid cart from this box office.</p>
      </div>
      {error && <p className="banner error">{error}</p>}
      {orders.length === 0 && !error && <p className="banner">No orders yet.</p>}
      <ul className="order-list">
        {orders.map((order) => (
          <li key={order.id}>
            <Link to={`/orders/${order.id}`}>
              <strong>
                #{order.id} · {buyer(order.user_id)}
              </strong>
              <span>
                {order.status} · {formatMoney(order.total_charged)} ·{" "}
                {formatWhen(order.created_at)}
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
