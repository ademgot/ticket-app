import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { Ticket } from "./api/types";

const STORAGE_KEY = "box-office-cart";

function readIds(): number[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as number[]) : [];
  } catch {
    return [];
  }
}

type CartContextValue = {
  ticketIds: number[];
  add: (ticket: Ticket) => void;
  remove: (ticketId: number) => void;
  clear: () => void;
  has: (ticketId: number) => boolean;
};

const CartContext = createContext<CartContextValue | null>(null);

export function CartProvider({ children }: { children: ReactNode }) {
  const [ticketIds, setTicketIds] = useState<number[]>(readIds);

  const persist = useCallback((ids: number[]) => {
    setTicketIds(ids);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
  }, []);

  const value = useMemo<CartContextValue>(
    () => ({
      ticketIds,
      add: (ticket) => {
        if (ticket.sold_at) return;
        persist(ticketIds.includes(ticket.id) ? ticketIds : [...ticketIds, ticket.id]);
      },
      remove: (ticketId) => persist(ticketIds.filter((id) => id !== ticketId)),
      clear: () => persist([]),
      has: (ticketId) => ticketIds.includes(ticketId),
    }),
    [persist, ticketIds],
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error("useCart must be used inside CartProvider");
  }
  return context;
}
