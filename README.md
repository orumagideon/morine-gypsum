# Morine Gypsum

Morine Gypsum is a full-stack store management and ordering platform built with a FastAPI backend and a React/Vite frontend. It supports product browsing, category management, cart and checkout flows, order history, admin management, invoices, email notifications, and MPESA payment verification helpers.

## What the project includes

- Public storefront for browsing products and categories
- Product detail and cart/checkout flow
- Customer order history and order details
- Admin dashboard for products, categories, and orders
- Backend APIs for authentication, products, categories, orders, and admin actions
- Static file serving for uploaded product images and generated invoices
- Optional email and MPESA-related backend support

## Tech stack

- Backend: FastAPI, SQLModel, SQLAlchemy, Uvicorn
- Database: PostgreSQL
- Frontend: React, Vite, Axios, React Router, Bootstrap
- Deployment helpers: Docker, Fly.io, Render

## Repository layout

- `app/` - FastAPI backend code, routers, models, schemas, services, and utilities
- `frontend/` - React application
- `docs/` - Deployment and integration guides
- `scripts/` - Admin and maintenance scripts

## Prerequisites

- Python 3.12 or compatible Python 3 version
- Node.js 18+ recommended
- PostgreSQL database

## Local setup

### 1. Configure environment variables

Copy `.env.example` to `.env` and fill in your values.

Required or commonly used variables:

- `DATABASE_URL` - PostgreSQL connection string
- `ALLOWED_ORIGINS` - Comma-separated frontend origins for CORS
- `VITE_API_BASE_URL` - Frontend API base URL
- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` - Optional email settings
- `SUPABASE_URL`, `SUPABASE_KEY` - Optional integration values if your deployment uses them

### 2. Start the backend

Install dependencies and run the API:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://127.0.0.1:8000`.

### 3. Start the frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend will usually run at `http://127.0.0.1:5173`.

## Key backend endpoints

- `GET /` - API welcome message
- `GET /health` - Health check
- `GET /products` - List products
- `GET /categories` - List categories
- `GET /orders` - Order endpoints
- `POST /admin/test-email` - Email test endpoint if SMTP is configured

## Deployment

The repo includes deployment configuration for Docker, Fly.io, and Render.

- See [docs/DEPLOY_BACKEND.md](docs/DEPLOY_BACKEND.md) for backend deployment steps
- See [docs/CONNECT_FRONTEND.md](docs/CONNECT_FRONTEND.md) for frontend-to-backend connection notes
- See [docs/EMAIL_AND_MPESA.md](docs/EMAIL_AND_MPESA.md) for email and MPESA-related behavior

Docker-based deployment uses the root [Dockerfile](Dockerfile) and exposes port `8080`.

## Data and migration notes

- The app creates and initializes database tables on startup
- Some order-related fields are managed through migration helpers in the repo
- If you need to repair or sync the database schema, see [DATABASE_FIX.md](DATABASE_FIX.md)

## Frontend API configuration

The frontend uses `frontend/src/api/axios.js` and reads `VITE_API_BASE_URL` at build time. If that variable is not set, it falls back to `http://127.0.0.1:8000`.

## Troubleshooting

- If the frontend cannot reach the backend, verify `VITE_API_BASE_URL` and `ALLOWED_ORIGINS`
- If uploads or invoices do not appear, check the `app/static/` directory permissions and your deployment platform's storage behavior
- If email features are disabled, confirm your SMTP settings are present and valid

## Related docs

- [docs/DEPLOY_BACKEND.md](docs/DEPLOY_BACKEND.md)
- [docs/CONNECT_FRONTEND.md](docs/CONNECT_FRONTEND.md)
- [docs/EMAIL_AND_MPESA.md](docs/EMAIL_AND_MPESA.md)
- [DATABASE_FIX.md](DATABASE_FIX.md)
