"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function SupportPage() {
  const [tickets, setTickets] = useState<Awaited<ReturnType<typeof api.tickets>> | null>(null);
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = () => api.tickets().then(setTickets).catch((e) => setError(e.message));

  useEffect(() => {
    refresh();
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!subject || !message) return;
    setSubmitting(true);
    setError(null);
    try {
      await api.createTicket(subject, message);
      setSubject("");
      setMessage("");
      await refresh();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1 className="font-display text-2xl text-paper mb-8">Support</h1>

      <form onSubmit={handleSubmit} className="border border-line rounded-sm p-4 mb-10 space-y-3">
        <input
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          placeholder="Subject"
          className="w-full bg-ink-raised border border-line text-paper text-sm rounded-sm px-3 py-2"
        />
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="How can we help?"
          rows={4}
          className="w-full bg-ink-raised border border-line text-paper text-sm rounded-sm px-3 py-2"
        />
        {error && <p className="text-red-400 text-xs">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="bg-brass text-ink text-sm font-medium px-4 py-2 rounded-sm disabled:opacity-50"
        >
          {submitting ? "Sending…" : "Send message"}
        </button>
      </form>

      <h2 className="font-mono text-xs text-mist tracking-widest mb-4">YOUR TICKETS</h2>
      <div className="space-y-2">
        {tickets?.map((t) => (
          <div key={t.id} className="flex justify-between items-center border-b border-line pb-2">
            <span className="text-paper text-sm">{t.subject}</span>
            <span className="font-mono text-xs text-brass uppercase">{t.status}</span>
          </div>
        ))}
        {tickets?.length === 0 && <p className="text-mist text-sm">No support tickets yet.</p>}
      </div>
    </div>
  );
}
