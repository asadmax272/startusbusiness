# StartUSBusiness — Platform Architecture

AI-powered USA business setup platform for non-US residents (UAE, Pakistan, India,
Bangladesh, Saudi Arabia, Qatar, Oman). This document is the map for the whole
build; everything under `/backend` and `/frontend` implements the pieces below.

## 1. Scope of this build (what's actually implemented now)

Given the size of the full spec, this first working version implements the
**foundation + flagship surfaces**, built to be extended, not a mockup:

- Postgres schema for all 12 core tables
- FastAPI backend: auth (JWT + Google OAuth stub), orders, documents,
  Stripe checkout + webhooks, AI Sales Assistant endpoint, AI Onboarding
  Agent endpoint — all using the real Claude API
- Role-based access (admin / staff / client)
- Docker Compose for local dev (Postgres + backend + frontend)
- Frontend: dark, premium homepage + pricing page + client dashboard shell,
  built with Next.js 15 / Tailwind, wired to the backend API
- Compliance-safe copy throughout ("application assistance", never
  "guaranteed approval") for Mercury/Stripe/Payoneer/EIN

**Update**: see `docs/AUDIT.md` for the full audit of this build against the
"complete SaaS" spec, and what was implemented in the follow-up pass (real
webhook → order/LLC/EIN creation, document upload/download, support tickets,
notifications, admin status updates, real email via Resend, client dashboard
UI). What's still not built: admin dashboard UI (API exists), blog CMS + 100
articles, AI Operations Agent as a background worker, CI/CD, rate limiting.

## 2. Tech stack

| Layer | Choice |
|---|---|
| Frontend | Next.js 15 (App Router), React, TypeScript, Tailwind CSS |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic |
| Database | PostgreSQL 16 |
| Auth | JWT (email/password) + Google OAuth |
| Payments | Stripe (Checkout + Billing + Webhooks) |
| Storage | Supabase Storage (S3-compatible) for documents |
| AI | Claude API (Anthropic) — Sales Assistant, Onboarding Agent, Ops Agent |
| Hosting | Vercel (frontend), VPS/Render/Fly.io (backend + Postgres) |
| Local dev | Docker Compose |

## 3. Folder structure

```
startusbusiness/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entrypoint
│   │   ├── core/                   # config, security, deps
│   │   ├── models/                 # SQLAlchemy models
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── api/                    # routers: auth, orders, documents,
│   │   │                           #   payments, ai, admin
│   │   ├── services/                # stripe.py, storage.py, email.py
│   │   └── agents/                  # sales_assistant.py, onboarding.py, ops.py
│   ├── migrations/                  # SQL schema
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # Homepage
│   │   ├── pricing/page.tsx
│   │   ├── dashboard/page.tsx       # Client dashboard shell
│   │   └── ...
│   ├── components/
│   ├── lib/                         # api client
│   └── Dockerfile
├── docker-compose.yml
└── docs/
    ├── ARCHITECTURE.md              # this file
    └── DEPLOYMENT.md
```

## 4. Database entities (see migrations/001_init.sql)

`users, orders, companies, documents, status_updates, messages, tickets,
payments, subscriptions, tasks, renewals, audit_logs` — matching the spec,
with foreign keys tying orders → companies → documents/status_updates, and
users → orders (client) / tasks (staff/admin).

## 5. AI system design

Three agents, all calling the Claude API server-side (never from the browser):

1. **Sales Assistant** (`/api/ai/sales-assistant`) — public-facing, runs the
   4-question flow (country, business type, payment processor, banking),
   then asks Claude to return a structured JSON recommendation (state,
   services, estimated cost, package). No account required.
2. **Onboarding Agent** (`/api/ai/onboarding`) — runs after checkout,
   collects and validates client-submitted data (name, passport, address,
   business name preferences) before it's attached to the order.
3. **Operations Agent** (`/api/ai/ops/*`) — internal, admin-triggered for now
   (cron/worker in the next phase): flags missing documents, drafts
   reminder emails, drafts support responses for staff to approve.

All AI endpoints require the response to be strict JSON (schema enforced in
the prompt + validated with Pydantic on the way out) so the frontend can
render it directly into UI, never raw model text for structured data.

## 6. Compliance guardrails (enforced in code + copy)

- No copy anywhere claims guaranteed approval for Mercury, Stripe, Payoneer,
  or EIN. Grep for "guarantee" in `/frontend` and `/backend` prompts as a
  pre-deploy check — see `docs/DEPLOYMENT.md`.
- Standard wording: "application assistance", "setup support", "guidance".

## 7. Next build phases (recommended order)

1. Remaining public pages (Wyoming LLC, EIN, Registered Agent, Seller
   Permit, Resale Certificate, US Phone Number, US Business Address) —
   mostly content + the same page template as the homepage.
2. Full client dashboard (LLC/EIN status trackers, document vault, invoices,
   renewal reminders) — API is ready, needs the UI built out.
3. Admin dashboard (users, orders, tickets, revenue reports, AI agent logs).
4. Blog/content hub + first 100 SEO articles + schema markup.
5. AI Operations Agent as a background worker (Celery/RQ + cron) instead of
   admin-triggered.
6. Production deployment: Vercel for frontend, VPS (Dockerized) or
   Render/Fly.io for backend + managed Postgres, secrets in a vault,
   Stripe live keys, Supabase Storage bucket policies.

Say which of these to build next and I'll build it the same way — real,
runnable code, not a stub.
