# Deployment Guide

## Local development

```bash
cp backend/.env.example backend/.env   # fill in ANTHROPIC_API_KEY and STRIPE keys at minimum
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000 (docs at /docs)
- Postgres: localhost:5432 (schema auto-loaded from `backend/migrations/001_init.sql`)

## Compliance pre-deploy check

Before every deploy, grep for prohibited absolute-approval language:

```bash
grep -rniE "guarantee(d)?\s+(approval|acceptance)" frontend backend | grep -v node_modules
```

This should return nothing. All Mercury/Stripe/Payoneer/EIN copy must use
"application assistance", "setup support", or "guidance" — never "guaranteed".

## Production

**Frontend (Vercel)**
1. Import the `frontend/` directory as a Vercel project.
2. Set `NEXT_PUBLIC_API_URL` to your backend's public URL.
3. Deploy — Vercel builds Next.js automatically.

**Backend (VPS or Render/Fly.io)**
1. Provision a managed Postgres instance; run `backend/migrations/001_init.sql` against it.
2. Set all vars from `.env.example` with production values (live Stripe keys,
   production Anthropic key, a strong `JWT_SECRET`).
3. Build and run `backend/Dockerfile` behind a reverse proxy (Caddy/Nginx) with TLS.
4. Point Stripe's webhook endpoint at `https://your-api-domain/api/payments/webhook`
   and copy the signing secret into `STRIPE_WEBHOOK_SECRET`.

**Secrets**: never commit `.env`. Use your host's secret manager (Vercel env
vars, Render/Fly secrets, or a vault) in production.

## Next build phases

See `docs/ARCHITECTURE.md` §7 for the recommended order of remaining work
(service pages, full dashboards, blog, Ops Agent worker, production hardening).
