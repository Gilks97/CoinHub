# Architecture

## Components

```
Customer browser
      │
      ▼
 Static frontend  (index.html, recharge.html, js/, css/, icons/)
      │  fetch() JSON
      ▼
 Django + Django REST Framework  (Gunicorn)
 ├── apps/catalog   CoinType model, pricing, GET /api/coins/
 ├── apps/orders    Order model, POST /api/recharges/, GET /api/payment-status/<ref>/
 ├── apps/payments  Payment model, Daraja client, POST /api/payments/daraja/callback/
 ├── apps/accounts  StaffProfile (role label for staff users)
 └── apps/core      base model, constants, utilities, admin CSS/JS
      │                          ▲
      ▼                          │ callback (HTTPS POST)
 PostgreSQL                 Safaricom Daraja ──► customer's phone (STK prompt)
```

## Two ways it runs

| | Local (compose) | Production (current) |
|---|---|---|
| Frontend served by | Nginx container, port 8080 | Render static site |
| Backend | Django container behind Nginx (`/api/`, `/admin/`) | Render web service (Docker) |
| Database | PostgreSQL container | Hosted PostgreSQL via `DATABASE_URL` |
| API base URL used by the frontend | `/api` (same origin, proxied by Nginx) | Full backend URL from `frontend/js/config.js` |

`frontend/js/config.js` decides which one applies: on `localhost` or `127.0.0.1` it uses `/api`; anywhere else it uses the backend URL written in the file.

## The apps

| App | Responsibility |
|---|---|
| `core` | `TimestampedModel` (created/updated fields), status constants, reference generation, admin CSS and JS (`static/coinhub_admin.*`) |
| `catalog` | `CoinType`: name, slug, price per 1,000 coins, conversion rate, icon, active flag |
| `orders` | `Order`: one recharge request; the public recharge and status endpoints; the admin "Ship Coins" workflow |
| `payments` | `Payment`: the STK transaction and audit payloads; Daraja client; callback handler |
| `accounts` | `StaffProfile`: a role label (SuperAdmin or Agent) attached to a staff user |

## Data model

```
CoinType 1 ──── * Order 1 ──── 1 Payment
                    │
                    └── loaded_by ──► auth.User (who shipped it)
```

### Order

| Field | Notes |
|---|---|
| `reference` | Unique, for example `CH2410260001` (`CH` + `DDMMYY` + 4-digit sequence) |
| `coin_type` | Foreign key, `PROTECT`: a coin with orders cannot be deleted |
| `app_user_id` | The customer's ID inside the external app (1 to 10 digits) |
| `phone_number` | M-Pesa number stored as `254XXXXXXXXX` |
| `coins_requested` | Multiple of 1,000, minimum 1,000 |
| `amount_paid` | KES amount calculated by the server |
| `status` | `pending`, `paid`, `loaded`, `failed` |
| `loaded_at`, `loaded_by`, `loading_notes` | Filled when staff ship the coins |

### Payment

Holds the M-Pesa side: `checkout_request_id`, `merchant_request_id`, `mpesa_receipt`, `result_code`, `result_description`, and three audit payloads (`request_payload`, `response_payload`, `callback_payload`) plus `callback_received_at`. Payments are read-only in the admin so the financial history cannot be edited.

## Status lifecycle

```
Order:    pending ──► paid ──► loaded
              └─────► failed

Payment:  pending ──► success
              └─────► failed   (cancelled exists as a status value)
```

| Transition | Triggered by |
|---|---|
| Order created as `pending`, Payment created as `pending` | `POST /api/recharges/` |
| Payment `success`, Order `paid` | Safaricom callback with `ResultCode` 0 |
| Payment `failed`, Order `failed` | Safaricom callback with any other result code |
| Order `loaded` | A staff member clicks **Ship Coins** (or uses the bulk action) after loading the coins |

Loading coins into the customer's app happens **outside CoinHub**. CoinHub only records that it was done, who did it and when.

## Recharge flow

1. The customer fills the form on `recharge.html` and the browser calls `POST /api/recharges/`.
2. The server validates the input and **calculates the price itself** (the browser's figure is only a preview and is never trusted).
3. The server creates the `Order` and `Payment` (both `pending`).
4. The server calls Daraja to send the STK Push to the customer's phone.
5. The customer enters their M-Pesa PIN.
6. Safaricom posts the result to `POST /api/payments/daraja/callback/`.
7. The callback handler updates the Payment and Order (atomically, and only once).
8. Meanwhile the browser polls `GET /api/payment-status/<reference>/` every 3 seconds, up to 20 times (about one minute), and shows success, failure or a timeout message.
9. Staff see the order as **Paid**, load the coins, and press **Ship Coins**.

See [Payments and Daraja](payments-daraja.md) for the details of steps 4 to 7.

## Pricing in one paragraph

Each coin stores a **price per 1,000 coins** in KES. The conversion rate (coins per 1 KES) is derived from it and rounded up. The payable amount is `ceil(coins / rate)`, a whole number of shillings, because STK Push cannot charge fractions. Details and examples: [Coin catalog](coin-catalog.md).

## Static files

Django collects admin assets into `staticfiles/` and WhiteNoise serves them in production. Locally Nginx also serves `/static/`. Custom admin styling and scripts are in `backend/apps/core/static/` and are loaded through the `custom_css` and `custom_js` Jazzmin settings.

## Design decisions worth knowing

| Decision | Reason |
|---|---|
| Price calculated on the server | Customers must not be able to change what they pay |
| Callback handler is atomic and idempotent | Safaricom can retry callbacks; the same payment must not be processed twice |
| Coins are loaded manually | The external apps are not integrated; staff load coins and then record it |
| `PROTECT` on `Order.coin_type` | Order history must always point to a real coin |
| Price per 1,000 stored on the coin, rate derived | Prices are edited in the admin without code changes |
