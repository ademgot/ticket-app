import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <main className="role-home">
      <div className="role-home__intro">
        <span className="brand-mark">BO</span>
        <p className="eyebrow">Box Office</p>
        <h1>How are you using the box office today?</h1>
        <p>Choose a workspace. You can return here and switch at any time.</p>
      </div>
      <div className="role-grid">
        <Link className="role-card role-card--user" to="/user">
          <span className="role-card__icon" aria-hidden="true">
            ♪
          </span>
          <div>
            <p className="eyebrow">Attendee</p>
            <h2>I'm buying tickets</h2>
            <p>Browse events, choose seats, check out, and review orders.</p>
          </div>
          <strong>Enter attendee view →</strong>
        </Link>
        <Link className="role-card role-card--organizer" to="/organizer">
          <span className="role-card__icon" aria-hidden="true">
            ✦
          </span>
          <div>
            <p className="eyebrow">Organizer</p>
            <h2>I'm running events</h2>
            <p>Create venues, events, seats, ticket inventory, buyers, and tax rates.</p>
          </div>
          <strong>Enter organizer view →</strong>
        </Link>
      </div>
    </main>
  );
}
