import { NavLink, Outlet } from "react-router-dom";
import { useCart } from "./cart";

type Role = "user" | "organizer";

export function Layout({ role }: { role: Role }) {
  const { ticketIds } = useCart();
  const isUser = role === "user";

  return (
    <div className={`app-view app-view--${role}`}>
      <div className="shell">
      <header className="masthead">
        <NavLink to={isUser ? "/user" : "/organizer"} className="brand">
          <span className="brand-mark">BO</span>
          <span>
            <strong>Box Office</strong>
            <em>{isUser ? "Attendee view" : "Organizer workspace"}</em>
          </span>
        </NavLink>
        <nav>
          {isUser ? (
            <>
              <NavLink to="/user" end>
                Events
              </NavLink>
              <NavLink to="/user/checkout">Cart ({ticketIds.length})</NavLink>
              <NavLink to="/user/orders">Orders</NavLink>
            </>
          ) : (
            <NavLink to="/organizer" end>
              Manage
            </NavLink>
          )}
          <NavLink to="/" end className="home-link">
            Switch role
          </NavLink>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
      </div>
    </div>
  );
}
