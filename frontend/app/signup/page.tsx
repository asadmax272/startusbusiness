"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { setToken } from "@/lib/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, full_name: fullName }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Signup failed.");
      const data = await res.json();
      setToken(data.access_token);
      router.push("/dashboard");
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-6">
      <form onSubmit={handleSubmit} className="w-full max-w-sm border border-line rounded-sm p-8 bg-ink-raised">
        <h1 className="font-display text-2xl text-paper mb-6">Create your account</h1>
        <div className="space-y-3">
          <input
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Full name"
            required
            className="w-full bg-ink border border-line text-paper text-sm rounded-sm px-3 py-2"
          />
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            type="email"
            placeholder="Email"
            required
            className="w-full bg-ink border border-line text-paper text-sm rounded-sm px-3 py-2"
          />
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            placeholder="Password"
            required
            minLength={8}
            className="w-full bg-ink border border-line text-paper text-sm rounded-sm px-3 py-2"
          />
        </div>
        {error && <p className="text-red-400 text-xs mt-3">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full mt-6 bg-brass text-ink font-medium py-2 rounded-sm disabled:opacity-50"
        >
          {loading ? "Creating account…" : "Create account"}
        </button>
        <p className="text-mist text-xs mt-4 text-center">
          Already have an account? <a href="/login" className="text-brass">Log in</a>
        </p>
      </form>
    </main>
  );
}
