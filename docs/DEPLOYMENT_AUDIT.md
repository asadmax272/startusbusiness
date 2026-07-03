# Deployment Audit — Railway + Vercel + Supabase

Traced against the actual repo, not the original spec. Each finding below
was verified by reading the exact code path; fixes applied in this pass are
marked ✅ FIXED, with the file changed.

## 1. Environment variables

- **Finding**: `config.py` used a legacy `class Config: env_file=".env"`
  block. `pydantic-settings` v2's supported pattern is
  `model_config = SettingsConfigDict(...)` — the old style is not reliably
  honored. On Railway this barely matters (env vars are injected directly
  into the process, no `.env` file involved), but it's a real inconsistency.
  ✅ FIXED — modernized to `SettingsConfigDict`.
- **Finding**: `JWT_SECRET` defaults to the literal string
  `"change-me-in-production"`. Nothing stopped the app from booting with
  that default in a real deployment. ✅ FIXED — app now refuses to start
  if `ENVIRONMENT=production` and `JWT_SECRET` is still the default.
- **Finding**: Supabase-specific env vars (`SUPABASE_URL`,
  `SUPABASE_SERVICE_ROLE_KEY`) didn't exist anywhere — storage was never
  actually wired to Supabase (see §4). ✅ FIXED — added.

## 2. Database migrations

- **Finding (real, would break deployment)**: migrations are plain `.sql`
  files under `backend/migrations/`, auto-applied only via Postgres's
  Docker image `/docker-entrypoint-initdb.d` convention in
  `docker-compose.yml`. **Railway's managed Postgres is a separate hosted
  service — it never runs that init mechanism.** Nothing would ever create
  the schema on a Railway database. `alembic` was in `requirements.txt` but
  never initialized (no `alembic.ini`, no `versions/`), so it wasn't doing
  anything either. ✅ FIXED — added `backend/scripts/migrate.py`, a small
  real migration runner: connects with `psycopg`, tracks applied files in a
  `schema_migrations` table, applies `.sql` files in order, is idempotent
  (safe to run on every deploy). Wired as the Railway deploy's release
  command (see checklist).

## 3. Stripe integration

- Webhook handler reads the raw request body before parsing
  (`await request.body()`) — correct; required for signature verification.
- No structural bugs found in checkout/webhook code itself.
- **Finding**: nothing enforces that `STRIPE_WEBHOOK_SECRET` matches a
  **live** vs **test** mode webhook endpoint — this is a config-time risk,
  not a code bug. Flagged in the checklist below (you configure one webhook
  endpoint per Stripe mode, each with its own secret).

## 4. Supabase storage

- **Finding (real, significant)**: despite `.env.example` listing
  `STORAGE_ENDPOINT` / `STORAGE_ACCESS_KEY` / etc., `storage.py` never read
  any of them — it only wrote to local disk. On Railway, container
  filesystems are ephemeral and not shared across instances or redeploys;
  every uploaded passport/document would be **silently lost** on the next
  deploy. This was the single most serious gap in the audit.
  ✅ FIXED — `storage.py` now has a real Supabase Storage implementation
  using Supabase's S3-compatible REST API (upload/download/delete via
  `httpx` against `{SUPABASE_URL}/storage/v1/object/...` with the
  **service role key**, which is required to bypass bucket RLS from the
  backend). Local-filesystem mode is kept only as an explicit dev fallback
  when `SUPABASE_URL` isn't set — so `docker-compose up` still works
  without a Supabase project.

## 5. Authentication

- UUID/str response-serialization bug (would have broken almost every
  authenticated GET endpoint) — already fixed in the previous pass.
- `bcrypt`/`passlib` version conflict, missing `email-validator` — already
  fixed in the previous pass.
- **Finding**: Google login is referenced in config (`google_client_id`)
  but there is **no OAuth route at all** — not even a stub. Email/password
  auth is real and works; Google login does not exist yet. Not silently
  claiming otherwise.
- **Finding**: no rate limiting on `/api/auth/login` or `/api/auth/signup`
  — brute-force/credential-stuffing exposure. ✅ FIXED — added a minimal
  in-memory rate limiter (per-IP, sliding window) on both endpoints. It's
  process-local, which is fine for a single Railway instance; if you scale
  to multiple instances, move this to a shared store (Redis) — noted in
  the checklist.

## 6. Security issues

- SQL access is 100% through the SQLAlchemy ORM query builder — no raw
  string interpolation found, no SQL injection surface.
- CORS credentials + wildcard methods/headers is spec-compliant as long as
  `allow_origins` isn't `"*"` (it isn't) — fine.
- **Finding**: no `.gitignore` existed. Pushing this repo to GitHub for
  Railway/Vercel's git-based deploys as-is risks committing `.env`,
  `node_modules`, `__pycache__`, and local dev storage. ✅ FIXED — added.
- **Finding**: no security headers (HSTS, X-Content-Type-Options,
  X-Frame-Options) set by the API. ✅ FIXED — added a small middleware.
- **Finding**: file upload only checks size and an allow-list of `type`
  values — it doesn't sniff actual file content. A renamed executable could
  be uploaded as a "passport". Acceptable for an MVP behind authenticated,
  staff-reviewed document flows, but flagged: add content-type sniffing or
  a malware-scan step before this handles real government ID documents at
  scale.
- **Finding**: `FROM_ADDRESS` in `email_service.py` was hardcoded to a
  placeholder domain. ✅ FIXED — now reads `EMAIL_FROM_ADDRESS` from env.

## 7. API routes

- All routers are registered in `main.py`; all paths consistently under
  `/api/*`. `/api/health` exists — needed for Railway's health check.
- No route-level bugs found beyond what's listed above.

## 8. CORS settings

- **Finding**: `allow_origins=[settings.frontend_url]` was a single hardcoded
  origin. Vercel preview deployments use per-branch/per-PR subdomains
  (`project-git-branch-team.vercel.app`) that would all be CORS-blocked
  under this setup. ✅ FIXED — `ALLOWED_ORIGINS` is now a comma-separated
  env var, and origins are matched with trailing slashes stripped.

## 9. Domain configuration

Covered entirely in the checklist below — this is a config/DNS task, not a
code issue, but two related **code** findings:
- Stripe webhook URL and `FRONTEND_URL` must be updated together when you
  attach a custom domain, or checkout redirects and CORS both break.
- `EMAIL_FROM_ADDRESS`'s domain must be verified in Resend (SPF/DKIM DNS
  records) before it will actually deliver — this is not a code bug, it's a
  DNS/Resend dashboard step, included in the checklist.
