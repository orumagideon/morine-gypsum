# Deploying the backend to Render

This file describes a simple way to deploy the `morine-gypsum` backend to Render using the included `render.yaml` manifest.

1) Connect your GitHub repo to Render
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service" (or choose to import from repo)
   - When asked, choose to import from GitHub and select `orumagideon/morine-gypsum`.

2) Use the `render.yaml` manifest
   - Render will detect `render.yaml` in the repository and pre-fill service settings.
   - The manifest configures a Docker-based Web Service named `morine-gypsum-backend` on branch `main`.

3) Add environment variables / secrets
   - Open the service settings → Environment → Environment Variables.
   - Add the following keys as *Private* (secret) values:
     - DATABASE_URL (example: `postgres://postgres:%40oruma.@ffmcjzrxtlgecjvlugpe.supabase.co:5432/postgres`)
     - SUPABASE_URL (example: `https://ffmcjzrxtlgecjvlugpe.supabase.co`)
     - SUPABASE_KEY (your Supabase server key)
     - ALLOWED_ORIGINS (example: `https://morine-gypsum.pages.dev`)
     - SMTP_HOST (optional)
     - SMTP_PORT (optional)
     - SMTP_USER (optional)
     - SMTP_PASSWORD (optional)
     - SMTP_FROM_EMAIL (optional)

   Notes:
   - If your database password contains special characters (like `@`), URL-encode them (e.g. `@` -> `%40`).
   - The application will normalize the DB scheme to include `psycopg2` and enable TLS for remote hosts.

4) Deploy and watch logs
   - After setting the env vars, trigger a deploy from the Render dashboard (or push to `main`).
   - Open the Logs tab for the service and watch startup. The server should bind to the port provided by Render and pass health checks.

5) Update frontend
   - When the backend is live, set `VITE_API_URL` in your Cloudflare Pages site to your Render service URL, e.g. `https://morine-gypsum-backend.onrender.com`.

Troubleshooting
 - If the service fails startup and logs show DB connection errors, double-check `DATABASE_URL` and ensure the Supabase project accepts external connections. Also confirm the `SUPABASE_KEY` is the server/service key and not the anon/public key.
 - If you see SSL/TLS issues, confirm `DATABASE_URL` is a proper postgres URL; the app will pass `sslmode=require` for remote connections.

Optional automation
 - I can add a GitHub Actions workflow that notifies Render (or triggers a redeploy) when `main` changes, or provide a `render.yaml`-driven setup script if you'd like.
