import { NavLink, Outlet } from "react-router-dom";
import { useCart } from "./cart";

export function Layout() {
  const { ticketIds } = useCart();

  return (
    <div className="shell">
      <header className="masthead">
        <NavLink to="/" className="brand">
          <span className="brand-mark">BO</span>
          <span>
            <strong>Box Office</strong>
            <em>Live seats, real inventory</em>
          </span>
        </NavLink>
        <nav>
          <NavLink to="/" end>
            Events
          </NavLink>
          <NavLink to="/checkout">Cart ({ticketIds.length})</NavLink>
          <NavLink to="/orders">Orders</NavLink>
          <NavLink to="/manage">Manage</NavLink>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
