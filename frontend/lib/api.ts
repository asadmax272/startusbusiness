const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("token");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export const api = {
  me: () => request<{ id: string; email: string; full_name: string; role: string }>("/api/auth/me"),
  orders: () => request<Array<{ id: string; package: string; services: string[]; status: string; amount_cents: number; created_at: string }>>("/api/orders"),
  llcStatus: (orderId: string) =>
    request<{ status: string; company_name: string; state: string; admin_notes: string | null; updated_at: string }>(
      `/api/orders/${orderId}/llc`
    ),
  einStatus: (orderId: string) =>
    request<{ status: string; ein_number: string | null; admin_notes: string | null; updated_at: string }>(
      `/api/orders/${orderId}/ein`
    ),
  documents: (orderId: string) =>
    request<Array<{ id: string; type: string; file_name: string; verified: boolean; created_at: string }>>(
      `/api/documents/order/${orderId}`
    ),
  tickets: () =>
    request<Array<{ id: string; subject: string; status: string; created_at: string }>>("/api/tickets"),
  createTicket: (subject: string, message: string, orderId?: string) =>
    request("/api/tickets", { method: "POST", body: JSON.stringify({ subject, message, order_id: orderId }) }),
  notifications: () =>
    request<Array<{ id: string; title: string; body: string; link: string | null; read_at: string | null; created_at: string }>>(
      "/api/notifications"
    ),
  unreadCount: () => request<{ count: number }>("/api/notifications/unread-count"),
};

export function setToken(token: string) {
  window.localStorage.setItem("token", token);
}

export function clearToken() {
  window.localStorage.removeItem("token");
}
