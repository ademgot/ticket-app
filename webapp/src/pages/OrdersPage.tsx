import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { pageUrl } from "../api/paging";
import type { Order, Page, User } from "../api/types";
import { Pager } from "../components/Pager";
import { formatMoney, formatWhen } from "../lib/format";

export function OrdersPage() {
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [orders, setOrders] = useState<Order[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.get<Page<Order>>(pageUrl("/orders/", page)),
      api.get<Page<User>>(pageUrl("/users/", 1)),
    ])
      .then(([orderPage, userPage]) => {
        setOrders(orderPage.items);
        setTotal(orderPage.total);
        setUsers(userPage.items);
        setError(null);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoaded(true));
  }, [page]);

  const buyer = (userId: number) =>
    users.find((user) => user.id === userId)?.name ?? `User #${userId}`;

  return (
    <section>
      <div className="page-head">
        <h1>Orders</h1>
        <p>Every paid cart from this ticket app.</p>
      </div>
      <Pager page={page} total={total} onPage={setPage} />
      {error && <p className="banner error">{error}</p>}
      {loaded && orders.length === 0 && !error && total === 0 && (
        <p className="banner">No orders yet.</p>
      )}
      <ul className="order-list">
        {orders.map((order) => (
          <li key={order.id}>
            <Link to={`/user/orders/${order.id}`}>
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
      <Pager page={page} total={total} onPage={setPage} />
    </section>
  );
}
