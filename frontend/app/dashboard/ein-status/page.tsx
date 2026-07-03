"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

const STAGES = ["pending", "submitted", "waiting_irs", "received", "completed"];

export default function EINStatusPage() {
  const [status, setStatus] = useState<Awaited<ReturnType<typeof api.einStatus>> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .orders()
      .then((orders) => {
        if (orders.length === 0) throw new Error("No orders yet.");
        return api.einStatus(orders[0].id);
      })
      .then(setStatus)
      .catch((e) => setError(e.message));
  }, []);

  const currentIndex = status ? STAGES.indexOf(status.status) : -1;

  return (
    <div>
      <h1 className="font-display text-2xl text-paper mb-8">EIN Status</h1>
      {error && (
        <p className="text-mist text-sm">
          {error === "No orders yet."
            ? "No orders yet."
            : "Your package doesn't include EIN assistance, or your order isn't set up yet."}
        </p>
      )}
      {!status && !error && <p className="text-mist text-sm">Loading…</p>}

      {status && (
        <>
          {status.ein_number && (
            <p className="font-mono text-brass text-lg mb-6">EIN: {status.ein_number}</p>
          )}
          <div className="flex items-center mb-8">
            {STAGES.map((stage, i) => (
              <div key={stage} className="flex items-center flex-1 last:flex-none">
                <div className={`w-3 h-3 rounded-full ${i <= currentIndex ? "bg-brass" : "bg-line"}`} />
                {i < STAGES.length - 1 && (
                  <div className={`h-px flex-1 ${i < currentIndex ? "bg-brass" : "bg-line"}`} />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between text-xs font-mono text-mist mb-8">
            {STAGES.map((s) => (
              <span key={s} className="capitalize">{s.replace("_", " ")}</span>
            ))}
          </div>
          {status.admin_notes && (
            <div className="border border-line rounded-sm p-4">
              <p className="font-mono text-xs text-mist mb-1">NOTE FROM YOUR FILING TEAM</p>
              <p className="text-paper text-sm">{status.admin_notes}</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
