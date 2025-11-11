Deploying the backend (FastAPI) — guide for Fly.io (recommended) and Render/Railway alternatives

This document explains the simplest, production-friendly steps to deploy your backend and connect it to Supabase Postgres. No secrets are stored in the repo.

Prerequisites
- You have a Supabase project and DATABASE_URL.
- You have pushed the repo to GitHub (done).

Recommended: Fly.io (free tier) — quick steps

1. Install flyctl

```bash
curl -L https://fly.io/install.sh | sh
export PATH="$HOME/.fly/bin:$PATH"
flyctl auth login
```

2. Initialize the Fly app

```bash
# From repo root
flyctl launch --name morine-gypsum-backend --region iad --no-deploy
```

This creates a `fly.toml` (you already have a template at repo root). Edit regions or app name if needed.

3. Set secrets (DO NOT commit these to git)

Replace the placeholders with your real values. Be careful to URL-encode the password in DATABASE_URL.

```bash
flyctl secrets set \
  DATABASE_URL='postgres://postgres:%40oruma.@ffmcjzrxtlgecjvlugpe.supabase.co:5432/postgres' \
  ALLOWED_ORIGINS='https://your-site.pages.dev' \
  SUPABASE_URL='https://ffmcjzrxtlgecjvlugpe.supabase.co' \
  SUPABASE_KEY='REPLACE_WITH_SUPABASE_KEY'
```

4. Deploy

```bash
flyctl deploy
```

5. Verify

- Get the app URL from the flyctl output or `flyctl status`.
- In Cloudflare Pages settings, set `VITE_API_URL` to the Fly app URL (https://...)
- Redeploy Pages or trigger a build so the frontend uses the new API URL.

Alternative: Render / Railway (UI-driven)

- Create a new Web Service on Render or Railway.
- Connect GitHub repo and point build to the repo root. Set the Start Command to use the Dockerfile or `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Add environment variables/secrets in the service settings: DATABASE_URL, ALLOWED_ORIGINS, SUPABASE_* , SMTP_* etc.

Notes: CORS and ALLOWED_ORIGINS
- We added environment-driven CORS: set `ALLOWED_ORIGINS` to a comma-separated list (e.g. `https://your-site.pages.dev,https://www.yourdomain.com`).

Object storage for invoices
- If you deploy to ephemeral containers, do not rely on local disk for invoices. Use Supabase Storage or Cloudflare R2 and set credentials as secrets.

If you want, I can generate a GitHub Actions workflow to automatically build and deploy to Fly when you push a commit — you will need to add `FLY_API_TOKEN` as a GitHub secret. Tell me if you want that and I will create the workflow file.
