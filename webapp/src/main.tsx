import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { CartProvider } from "./cart";
import { Layout } from "./Layout";
import { CheckoutPage } from "./pages/CheckoutPage";
import { EventPage } from "./pages/EventPage";
import { EventsPage } from "./pages/EventsPage";
import { HomePage } from "./pages/HomePage";
import { ManagePage } from "./pages/ManagePage";
import { OrderPage } from "./pages/OrderPage";
import { OrdersPage } from "./pages/OrdersPage";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <CartProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route element={<Layout role="user" />}>
            <Route path="/user" element={<EventsPage />} />
            <Route path="/user/events/:eventId" element={<EventPage />} />
            <Route path="/user/checkout" element={<CheckoutPage />} />
            <Route path="/user/orders" element={<OrdersPage />} />
            <Route path="/user/orders/:orderId" element={<OrderPage />} />
          </Route>
          <Route element={<Layout role="organizer" />}>
            <Route path="/organizer" element={<ManagePage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </CartProvider>
  </StrictMode>,
);
