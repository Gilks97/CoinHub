# Security

CoinHub handles real money and customer phone numbers. This page lists what is in place, what is not yet, and what to do first.

## Implemented

| Area | Measure |
|---|---|
| Secrets | Read from environment variables; `.env` is git-ignored; only `.env.example` is committed |
| Pricing | The server calculates every price; the browser's figure is only a preview |
| Input validation | Coin must be active; User ID 1 to 10 digits; valid Kenyan phone; coins in multiples of 1,000 |
| Callback integrity | Atomic transaction with a row lock; already-final payments are ignored (safe against retries) |
| Audit | Request, response and callback payloads stored on each payment; Payments admin is read-only |
| Transport | With `DEBUG=False`: HTTPS redirect, secure session and CSRF cookies, proxy SSL header |
| Database | SSL required when `DEBUG=False` |
| API surface | JSON only; token authentication class configured; anonymous throttling |
| Data protection | Orders cannot lose their coin (`PROTECT`); coin deletion is superuser-only |
| Static files | Served by WhiteNoise / Nginx |

## Known gaps and hardening roadmap

These were identified in a code review. Treat the first group as required before significant real-money traffic.

### Critical

1. **The callback is unauthenticated and does not verify the payment details.** Anyone who knows a `CheckoutRequestID` could post a fake success. Fix:
   - put a long random secret in the callback URL and keep it in an environment variable,
   - compare the callback's `Amount` and `PhoneNumber` with the payment before marking it paid,
   - confirm with Daraja's STK Query before releasing an order,
   - consider an allowlist of Safaricom source addresses (get the current list from Daraja support),
   - make `mpesa_receipt` unique.
2. **Anyone can trigger STK prompts to any phone number.** Add per-phone and per-IP limits (for example a few per hour per number), a CAPTCHA such as Cloudflare Turnstile, a maximum coin amount, and a guard against duplicate pending orders for the same phone.
3. **Order references are sequential and the status endpoint is public.** References can be enumerated, exposing User IDs and amounts. Use an unguessable public identifier for the status URL and return only what the page needs.
4. **Startup script risks.** `docker/entrypoint.sh` runs `makemigrations` on every start (remove it) and ignores superuser creation errors. Make the superuser step require explicit environment variables, with no default password anywhere.

### High

5. **A failed STK initiation still returns "payment initiated".** Mark the order failed and return an error so the customer is not left waiting.
6. **`checkout_request_id` is not unique.** Make it unique so a callback always matches exactly one payment.
7. **Reference generation can collide under concurrent requests.** Use a random suffix or retry on conflict.
8. **Sensitive data in logs.** Request bodies (phone numbers, User IDs) and Daraja error bodies are logged. Mask phone numbers and log only what is needed.
9. **Dependencies are outdated.** Django 5.0 is past end of life. Upgrade to a supported release and run `pip-audit` regularly. Remove unused packages (for example `djangorestframework-simplejwt`).

### Medium

10. **Rate limits are shared and low.** Public endpoints share one 100-per-day anonymous limit. Use separate limits for creating payments and for status polling.
11. **Admin hardening.** Move `/admin/` off the default path, add two-factor authentication (`django-otp`) and login lockout (`django-axes`).
12. **User and group deletion** is governed only by Django permissions. Restrict deletion of users and groups to superusers, and keep add/change of users and groups superuser-only so nobody can grant themselves superuser rights.
13. **Reconciliation.** Add a scheduled job that re-checks `pending` payments with STK Query.
14. **Headers.** Add HSTS settings, set `CORS_ALLOW_CREDENTIALS = False` (no cookies are used by the public API), and add security headers (CSP, `X-Content-Type-Options`, `Referrer-Policy`) on the static frontend.
15. **Container.** Run as a non-root user.
16. **Amount arithmetic.** Use `Decimal` end to end for money (the browser preview uses floating point).

### Frontend

17. Build page elements with `textContent` or DOM APIs instead of `innerHTML` for data that comes from the API.

## Handling secrets

- Rotate credentials immediately if they were ever pasted into Git, a chat, a screenshot or a public issue (Daraja key and secret, passkey, database password, `SECRET_KEY`, superuser password).
- Scan history with a tool such as `gitleaks` before making a repository public.
- Production secrets live only in the hosting dashboard.
- Never use the example superuser password anywhere real.

## Customer data

Orders and payments store phone numbers, App User IDs and M-Pesa receipts. Restrict admin access to people who need it, keep database backups protected, and do not share exports or screenshots publicly.

## If something goes wrong

| Situation | Action |
|---|---|
| Suspected fake or duplicate payments | Compare payments with the till statement; review `callback_payload` on the payments; check logs |
| Leaked credentials | Rotate them in Daraja and the hosting dashboard, redeploy, review recent activity |
| Staff account misuse | Deactivate the user (do not delete), review "loaded by" history on orders |

## Reporting a vulnerability

Contact the project maintainer privately. Do not open a public issue with exploit details or any customer data.
