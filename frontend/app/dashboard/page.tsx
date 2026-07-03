"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function OverviewPage() {
  const [orders, setOrders] = useState<Awaited<ReturnType<typeof api.orders>> | null>(null);
  const [notifications, setNotifications] = useState<Awaited<ReturnType<typeof api.notifications>> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.orders(), api.notifications()])
      .then(([o, n]) => {
        setOrders(o);
        setNotifications(n);
      })
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="text-red-400 text-sm">
        Couldn't load your dashboard: {error}. Try signing in again.
      </div>
    );
  }

  return (
    <div>
      <h1 className="font-display text-2xl text-paper mb-8">Overview</h1>

      <section className="mb-10">
        <h2 className="font-mono text-xs text-mist tracking-widest mb-4">RECENT ORDERS</h2>
        {orders === null && <p className="text-mist text-sm">Loading…</p>}
        {orders?.length === 0 && (
          <p className="text-mist text-sm">
            No orders yet. <a href="/pricing" className="text-brass">Start your LLC</a>.
          </p>
        )}
        <div className="space-y-3">
          {orders?.map((o) => (
            <a
              key={o.id}
              href={`/dashboard/orders`}
              className="block border border-line rounded-sm p-4 hover:border-steel transition-colors"
            >
              <div className="flex justify-between items-center">
                <span className="text-paper font-display capitalize">{o.package} Package</span>
                <span className="font-mono text-xs text-brass uppercase">{o.status.replace("_", " ")}</span>
              </div>
              <span className="text-mist text-xs">${(o.amount_cents / 100).toFixed(2)}</span>
            </a>
          ))}
        </div>
      </section>

      <section>
        <h2 className="font-mono text-xs text-mist tracking-widest mb-4">NOTIFICATIONS</h2>
        {notifications === null && <p className="text-mist text-sm">Loading…</p>}
        {notifications?.length === 0 && <p className="text-mist text-sm">You're all caught up.</p>}
        <div className="space-y-2">
          {notifications?.map((n) => (
            <div key={n.id} className="border-b border-line pb-2">
              <p className="text-paper text-sm">{n.title}</p>
              <p className="text-mist text-xs">{n.body}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
