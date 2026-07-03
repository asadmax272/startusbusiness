# Deployment Checklist — Railway (backend) + Vercel (frontend) + Supabase (DB + storage)

Do these in order — later steps need values produced by earlier ones.

## 1. Supabase project

- [ ] Create a Supabase project. Note the project URL and the **service
      role key** (Project Settings → API) — not the anon key, the backend
      needs elevated access to bypass storage RLS.
- [ ] Database → get the Postgres connection string (Session pooler, port
      6543, or the direct connection on 5432 — use the pooler for the app).
      This becomes `DATABASE_URL` (converted to `postgresql+psycopg://...`).
- [ ] Storage → create a bucket named `startusbusiness-documents` (or
      whatever you set `STORAGE_BUCKET` to). Keep it **private** — documents
      are passports/IDs; the backend accesses it with the service role key,
      never the anon key, so no public bucket policy is needed.

## 2. Railway (backend)

- [ ] New Railway project → deploy from this repo, root directory `backend/`.
- [ ] Set environment variables (Railway → Variables): every var listed in
      `backend/.env.example` — with real values:
  - `ENVIRONMENT=production`
  - `DATABASE_URL` — from Supabase, converted to `postgresql+psycopg://...`
  - `JWT_SECRET` — generate a real random value (`openssl rand -hex 32`).
    The app will refuse to boot in production with the placeholder — this
    is intentional, not a bug.
  - `ALLOWED_ORIGINS` — your Vercel production domain, comma-separated with
    any other origins you need (see §5).
  - `FRONTEND_URL` — your Vercel production domain (used in Stripe
    redirect URLs).
  - `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` — from Stripe (§4).
  - `ANTHROPIC_API_KEY` — from the Anthropic Console.
  - `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `STORAGE_BUCKET` — from
    step 1. Do **not** leave these empty in production — without them,
    document uploads fall back to local disk and will be lost on the next
    deploy (see `docs/DEPLOYMENT_AUDIT.md` §4).
  - `RESEND_API_KEY`, `EMAIL_FROM_ADDRESS` — from Resend (§6).
- [ ] Set the **release command** (Railway → Settings → Deploy) to:
      `python scripts/migrate.py` — this applies the SQL migrations against
      the real Supabase database on every deploy (see `docs/DEPLOYMENT_AUDIT.md`
      §2 for why this step is required and not automatic).
- [ ] Set the **start command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
      (Railway injects `$PORT` — don't hardcode 8000).
- [ ] Health check path: `/api/health`.
- [ ] Deploy. Note the generated `*.up.railway.app` URL (or attach a custom
      domain — see §7).

## 3. Vercel (frontend)

- [ ] Import the repo, root directory `frontend/`.
- [ ] Environment variable: `NEXT_PUBLIC_API_URL` = your Railway backend URL
      (from §2). Set it for Production, Preview, and Development
      environments separately if they point at different backends.
- [ ] Deploy.

## 4. Stripe

- [ ] Create Products/Prices matching `backend/app/core/packages.py` if you
      want them to also appear in the Stripe Dashboard (the app itself
      creates prices dynamically via `price_data`, so this is optional but
      recommended for reporting).
- [ ] Developers → Webhooks → Add endpoint:
      `https://<your-railway-domain>/api/payments/webhook`, event:
      `checkout.session.completed`. Copy the signing secret into
      `STRIPE_WEBHOOK_SECRET` on Railway.
- [ ] Use **test mode** keys/webhook until you've verified a full checkout
      end-to-end, then switch to live mode keys + a **second**, separate
      live-mode webhook endpoint with its own signing secret.

## 5. CORS

- [ ] `ALLOWED_ORIGINS` on Railway must include your Vercel production
      domain exactly (no trailing slash — the app strips one if present,
      but double-check). If you need preview deployments to also call the
      API, add each preview domain you use, or switch Vercel to a fixed
      preview alias.

## 6. Resend (email)

- [ ] Add and verify your sending domain in Resend (Domains → Add Domain),
      add the SPF/DKIM DNS records it gives you at your DNS provider.
- [ ] Set `EMAIL_FROM_ADDRESS` on Railway to an address on that verified
      domain, e.g. `StartUSBusiness <notifications@yourdomain.com>`. Emails
      will fail to send from an unverified domain.

## 7. Domain configuration

- [ ] Frontend custom domain: Vercel → Domains → add your domain, follow
      the CNAME/A record instructions.
- [ ] Backend custom domain (optional but recommended): Railway →
      Settings → Domains → add a custom domain (e.g. `api.yourdomain.com`),
      add the CNAME Railway gives you.
- [ ] After attaching custom domains, update on Railway:
  - `FRONTEND_URL` → the new frontend domain
  - `ALLOWED_ORIGINS` → include the new frontend domain
  and on Vercel:
  - `NEXT_PUBLIC_API_URL` → the new backend domain
  and in Stripe:
  - update the webhook endpoint URL to the new backend domain
  These four have to change together — missing one breaks checkout
  redirects, CORS, or webhook delivery respectively.

## 8. Post-deploy smoke test (do this for real, in the live environment)

- [ ] Sign up a test account → confirm a welcome email arrives.
- [ ] Log in.
- [ ] Run the AI Sales Assistant flow → confirm a recommendation comes back.
- [ ] Checkout with a Stripe test card (`4242 4242 4242 4242`) → confirm
      you land on `/dashboard?checkout=success` and an Order/LLC
      application actually appears (this proves the webhook + release-
      command migration both worked).
- [ ] Upload a test document → confirm it appears in the Supabase Storage
      bucket dashboard, not just in the app.
- [ ] Open a support ticket → confirm it's listed via `/api/admin/tickets`
      for an admin-role account.

## 9. Ongoing

- [ ] Rotate `JWT_SECRET` invalidates all sessions if you ever need to force
      logout everywhere (e.g. after a suspected leak).
- [ ] The in-memory rate limiter (`app/core/rate_limit.py`) is per-instance.
      If you scale Railway to multiple replicas, move it to Redis or a
      Railway-provided KV store — right now each replica has its own
      independent counter.
