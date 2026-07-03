"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Packages = Record<string, { label: string; price_cents: number; services: string[]; description: string }>;

export default function PricingPage() {
  const [packages, setPackages] = useState<Packages | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [checkingOut, setCheckingOut] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/packages`)
      .then((r) => r.json())
      .then((d) => setPackages(d.packages))
      .catch(() => setError("Couldn't load pricing right now."));
  }, []);

  async function handleCheckout(packageId: string) {
    const token = window.localStorage.getItem("token");
    if (!token) {
      window.location.href = "/signup";
      return;
    }
    setCheckingOut(packageId);
    try {
      const res = await fetch(`${API_URL}/api/payments/checkout/${packageId}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Checkout failed.");
      const data = await res.json();
      window.location.href = data.checkout_url;
    } catch (e: any) {
      setError(e.message);
      setCheckingOut(null);
    }
  }

  return (
    <main className="min-h-screen max-w-6xl mx-auto px-6 py-16">
      <h1 className="font-display text-3xl text-paper mb-2">Pricing</h1>
      <p className="text-mist mb-10">
        Every package includes Wyoming LLC formation. Banking and payment
        processor items are application assistance — approval is decided by
        the bank or processor, never guaranteed.
      </p>
      {error && <p className="text-red-400 text-sm mb-6">{error}</p>}
      {!packages && !error && <p className="text-mist text-sm">Loading…</p>}
      <div className="grid md:grid-cols-4 gap-4">
        {packages &&
          Object.entries(packages).map(([id, pkg]) => (
            <div key={id} className="border border-line rounded-sm p-6 flex flex-col">
              <p className="font-display text-xl text-paper mb-1">{pkg.label}</p>
              <p className="text-mist text-xs mb-4">{pkg.description}</p>
              <p className="font-mono text-2xl text-brass mb-6">${(pkg.price_cents / 100).toFixed(0)}</p>
              <ul className="text-sm text-paper space-y-1.5 mb-6 flex-1">
                {pkg.services.map((s) => (
                  <li key={s}>✓ {s.replace(/_/g, " ")}</li>
                ))}
              </ul>
              <button
                onClick={() => handleCheckout(id)}
                disabled={checkingOut === id}
                className="bg-brass text-ink font-medium py-2 rounded-sm disabled:opacity-50"
              >
                {checkingOut === id ? "Redirecting…" : "Choose plan"}
              </button>
            </div>
          ))}
      </div>
    </main>
  );
}
