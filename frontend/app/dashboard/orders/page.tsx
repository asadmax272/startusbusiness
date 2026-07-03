"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function OrdersPage() {
  const [orders, setOrders] = useState<Awaited<ReturnType<typeof api.orders>> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.orders().then(setOrders).catch((e) => setError(e.message));
  }, []);

  return (
    <div>
      <h1 className="font-display text-2xl text-paper mb-8">Orders</h1>
      {error && <p className="text-red-400 text-sm">{error}</p>}
      {orders === null && !error && <p className="text-mist text-sm">Loading…</p>}
      <div className="space-y-3">
        {orders?.map((o) => (
          <div key={o.id} className="border border-line rounded-sm p-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-paper font-display capitalize">{o.package} Package</span>
              <span className="font-mono text-xs text-brass uppercase">{o.status.replace("_", " ")}</span>
            </div>
            <p className="text-mist text-xs mb-2">
              {new Date(o.created_at).toLocaleDateString()} · ${(o.amount_cents / 100).toFixed(2)}
            </p>
            <div className="flex flex-wrap gap-2">
              {o.services.map((s) => (
                <span key={s} className="text-xs font-mono text-mist bg-ink-raised px-2 py-1 rounded-sm">
                  {s}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
