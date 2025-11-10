Email & MPESA Configuration

This document explains how to enable admin email notifications and test the MPESA STK push flow (Pochi simulation supported).

1) Email notifications (backend)

- The project uses `app/services/email_service.py` and the standard SMTP protocol to send emails.
- By default the service will not send emails unless `SMTP_PASSWORD` environment variable is set (to avoid accidental exposure).

Required environment variables (recommended):

- SMTP_SERVER (default: smtp.gmail.com)
- SMTP_PORT (default: 587)
- SMTP_USERNAME (your SMTP login, e.g. your Gmail address)
- SMTP_PASSWORD (app-specific password or SMTP password)

Example (bash):

```bash
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USERNAME=you@example.com
export SMTP_PASSWORD=your-app-password
```

- There is a convenient admin endpoint to test email delivery once SMTP is configured:
  POST /admin/test-email with JSON body { "to_email": "you@domain.com", "subject": "Test", "body": "Hello" }

Notes:
- If you don't want to configure SMTP, the app will log the intended email contents to stdout and return false from the send function. Configure SMTP for real delivery. For production we recommend using a dedicated transactional email provider (SendGrid, Mailgun, Amazon SES) and storing credentials in your environment or a secrets manager.

2) MPESA / Pochi flow (server + frontend)

Implemented features:
- Server endpoints (FastAPI):
  - POST /orders/{order_id}/mpesa/push  -> Initiate STK Push (simulated if no external provider configured). Request body: { "phone_number": "07...", "amount": 1234 }
  - GET  /orders/{order_id}/mpesa/status -> Pollable payment status. Returns { payment_verified, payment_status, mpesa_request_id, mpesa_code }
  - POST /orders/mpesa/webhook -> Provider webhook to notify payment confirmation. Body: { order_id, mpesa_code, phone_number, status }
  - Existing endpoint POST /orders/{order_id}/verify-payment still accepts manual MPESA confirmation codes (for manual verification).

- Frontend (React):
  - `MpesaVerification.jsx` now supports:
    - Requesting an STK Push (one-tap) via the new `/orders/{order_id}/mpesa/push` endpoint.
    - Polling `/orders/{order_id}/mpesa/status` every 5s to detect when the payment has been verified (so the user doesn't need to paste the code).
    - A fallback manual confirmation input (enter MPESA confirmation code) remains available.

How to test locally (no real MPESA provider):

1. Place an order selecting MPESA as payment method.
2. On the MPESA verification step, click "Request STK Push (One-tap)". The backend will simulate an STK request and return a simulated request id.
3. The frontend will poll the status endpoint. To simulate a successful payment, POST to the webhook endpoint with the order id:

```bash
# Example (use httpie or curl)
curl -X POST http://localhost:8000/orders/mpesa/webhook \
  -H 'Content-Type: application/json' \
  -d '{"order_id": 123, "mpesa_code": "SIM12345", "phone_number": "0700...", "status": "SUCCESS"}'
```

4. The frontend polling will detect the status change and automatically mark the order as paid and continue the checkout flow.

Testing webhook from outside (ngrok):
- Start your backend with a public URL via ngrok (or similar):
  ngrok http 8000
- Configure your MPESA/Pochi provider to send callbacks to https://<your-ngrok-id>.ngrok.io/orders/mpesa/webhook

3) Notes & Next steps
- For production STK Push integration you will need real credentials for your MPESA provider (Safaricom Daraja, Pochi or a third-party aggregator). Add configuration values to `app_settings.json` or environment and extend the `initiate_mpesa_push` handler to call the provider's API and persist their request id.
- The `order.mpesa_request_id` column was added to the model and an idempotent ALTER is applied at startup by `app/db/init_db.py`.
- Emails and webhooks should be secured in production (validate payload signatures, use TLS, store credentials securely).

If you want, I can:
- Add a small admin UI to trigger webhooks for testing.
- Integrate a specific MPESA provider SDK (if you provide credentials) and implement STK Push calls and signature verification.
