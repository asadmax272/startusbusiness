import RouteSeal from "@/components/RouteSeal";

const SERVICE_LINES = [
  { n: "01", label: "Wyoming LLC Formation" },
  { n: "02", label: "EIN Application Assistance" },
  { n: "03", label: "Registered Agent Service" },
  { n: "04", label: "US Business Address" },
  { n: "05", label: "US Phone Number" },
  { n: "06", label: "Mercury Application Support" },
];

const COUNTRIES = ["UAE", "Pakistan", "India", "Bangladesh", "Saudi Arabia", "Qatar", "Oman"];

export default function HomePage() {
  return (
    <main className="min-h-screen">
      {/* Nav */}
      <header className="border-b border-line">
        <nav className="max-w-6xl mx-auto flex items-center justify-between px-6 py-5">
          <span className="font-display font-700 text-lg tracking-tight text-paper">
            StartUSBusiness
          </span>
          <div className="hidden md:flex items-center gap-8 text-sm text-mist">
            <a href="/services" className="hover:text-paper transition-colors">Services</a>
            <a href="/pricing" className="hover:text-paper transition-colors">Pricing</a>
            <a href="/blog" className="hover:text-paper transition-colors">Blog</a>
            <a href="/faq" className="hover:text-paper transition-colors">FAQ</a>
          </div>
          <a
            href="/pricing"
            className="text-sm font-medium bg-brass text-ink px-4 py-2 rounded-sm hover:bg-brass-dim transition-colors"
          >
            Start Your LLC
          </a>
        </nav>
      </header>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-16 pb-20 grid md:grid-cols-2 gap-12 items-center">
        <div>
          <p className="font-mono text-xs text-brass tracking-widest mb-4">
            FILED FROM {COUNTRIES.length}+ COUNTRIES
          </p>
          <h1 className="font-display font-700 text-4xl md:text-5xl leading-tight text-paper">
            Start Your US Business
            <br />
            From Anywhere
          </h1>
          <p className="mt-5 text-mist text-lg max-w-md">
            AI-powered USA business setup for founders from UAE, Pakistan, India,
            and worldwide — Wyoming LLC formation with EIN, banking, and
            compliance support handled for you.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <a
              href="/pricing"
              className="bg-brass text-ink font-medium px-6 py-3 rounded-sm hover:bg-brass-dim transition-colors"
            >
              Start Your LLC
            </a>
            <a
              href="#ai-assistant"
              className="border border-line text-paper font-medium px-6 py-3 rounded-sm hover:border-steel transition-colors"
            >
              Talk to AI Assistant
            </a>
          </div>
          <p className="mt-6 text-xs text-mist max-w-md">
            Application assistance for EIN, Mercury, Stripe, and Payoneer — outcomes
            depend on the provider's own review and are never guaranteed.
          </p>
        </div>
        <RouteSeal />
      </section>

      {/* Service docket */}
      <section className="border-t border-line bg-ink-raised">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <p className="font-mono text-xs text-mist tracking-widest mb-8">SERVICES ON FILE</p>
          <div className="grid md:grid-cols-2 gap-x-12 gap-y-6">
            {SERVICE_LINES.map((s) => (
              <div key={s.n} className="flex items-baseline gap-4 border-b border-line pb-4">
                <span className="font-mono text-brass text-sm">{s.n}</span>
                <span className="font-display text-paper text-lg">{s.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* AI assistant teaser */}
      <section id="ai-assistant" className="max-w-6xl mx-auto px-6 py-20">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <p className="font-mono text-xs text-brass tracking-widest mb-4">AI SALES ASSISTANT</p>
            <h2 className="font-display font-600 text-3xl text-paper mb-4">
              Four questions. One recommendation.
            </h2>
            <p className="text-mist mb-6">
              Tell the assistant your country, business type, and what you need
              for payments and banking — it recommends a state, service list,
              and estimated cost in seconds.
            </p>
            <ul className="space-y-2 text-sm text-mist font-mono">
              <li>→ Which country are you from?</li>
              <li>→ What type of business are you starting?</li>
              <li>→ Do you need payment processing?</li>
              <li>→ Do you need business banking?</li>
            </ul>
          </div>
          <div className="border border-line rounded-sm p-6 bg-ink-raised">
            <p className="font-mono text-xs text-mist mb-3">SAMPLE RECOMMENDATION</p>
            <p className="font-display text-paper text-xl mb-4">Business Package</p>
            <ul className="text-sm text-paper space-y-1.5">
              <li>✓ Wyoming LLC</li>
              <li>✓ EIN Assistance</li>
              <li>✓ Registered Agent</li>
              <li>✓ US Business Address</li>
              <li>✓ Mercury Support</li>
            </ul>
            <p className="mt-4 text-brass font-mono text-sm">Est. $299</p>
          </div>
        </div>
      </section>

      {/* Countries footer strip */}
      <section className="border-t border-line">
        <div className="max-w-6xl mx-auto px-6 py-10 flex flex-wrap gap-x-8 gap-y-2 text-sm text-mist font-mono">
          {COUNTRIES.map((c) => (
            <span key={c}>{c}</span>
          ))}
        </div>
      </section>

      <footer className="border-t border-line">
        <div className="max-w-6xl mx-auto px-6 py-10 text-xs text-mist flex flex-wrap justify-between gap-4">
          <span>© {new Date().getFullYear()} StartUSBusiness</span>
          <div className="flex gap-6">
            <a href="/terms" className="hover:text-paper">Terms</a>
            <a href="/privacy" className="hover:text-paper">Privacy Policy</a>
            <a href="/contact" className="hover:text-paper">Contact</a>
          </div>
        </div>
      </footer>
    </main>
  );
}
