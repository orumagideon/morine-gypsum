Linking Cloudflare Pages frontend to Render backend

This file shows the exact steps to connect your deployed frontend (Cloudflare Pages) to your deployed backend (Render).

1) Backend (Render) — set environment variables

Open your Render dashboard > Services > morine-gypsum-backend > Environment. Add these env vars (private values):

- DATABASE_URL
  Example: postgres://postgres:oruma@ffmcjzrxtlgecjvlugpe.supabase.co:5432/postgres

- SUPABASE_URL
  Example: https://ffmcjzrxtlgecjvlugpe.supabase.co

- SUPABASE_KEY
  (Service role key or anon key depending on server usage)

- ALLOWED_ORIGINS
  Comma-separated list of frontend origins. Example:
  https://morine-gypsum.pages.dev, http://localhost:5173

- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_EMAIL
  (If you use email features)

Optional (allows any Cloudflare Pages branch subdomain):
- ALLOW_PAGES_WILDCARD=true

After adding these, redeploy the service (Render will often auto-deploy).

2) Frontend (Cloudflare Pages) — set build environment variable

Open your Cloudflare Pages project > Settings > Environment variables.
Add the variable used by the frontend build:

- VITE_API_BASE_URL
  Value: https://<your-render-service>.onrender.com
  Example: https://morine-gypsum-4.onrender.com

Then re-deploy your Pages site (trigger a new build). The compiled frontend will use this value at runtime.

3) CORS and credentials

- The backend reads `ALLOWED_ORIGINS` for CORS and also supports an optional Pages wildcard via `ALLOW_PAGES_WILDCARD=true`.
- If your frontend uses cookies/auth sessions, set `withCredentials: true` in frontend axios and keep `allow_credentials=True` on the backend. Also ensure both sides use HTTPS.

4) Quick verification

- Curl backend root (no CORS involved):
  curl -i https://morine-gypsum-4.onrender.com/

- From your browser (frontend), open DevTools -> Network, then use the site and confirm API requests are 200. If you see CORS errors in the console, ensure the origin is listed in `ALLOWED_ORIGINS`.

5) Troubleshooting

- If Render logs show the app connecting to `localhost`, double-check the Render `DATABASE_URL` secret value and that it's not empty.
- If you need me to tail Render logs while you update secrets, paste the Render Live URL and I will guide you.

If you'd like, I can also add a tiny GitHub Actions workflow to automatically set Cloudflare Pages envs or trigger a Pages redeploy after backend deploys. Let me know which automation you'd prefer.
