# API reference

Base path: `/api/`. All endpoints use JSON. There are no user accounts for customers, so the public endpoints need no token. Every endpoint is subject to the rate limits in [Configuration](configuration.md).

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/coins/` | List active coins and their rates |
| POST | `/api/recharges/` | Create an order and start the STK Push |
| GET | `/api/payment-status/<reference>/` | Poll an order's status |
| POST | `/api/payments/daraja/callback/` | Safaricom's result callback (not for browsers) |

---

## GET /api/coins/

Returns active coins only (inactive coins are hidden).

```json
[
  {
    "id": 1,
    "name": "Baat",
    "slug": "baat",
    "conversion_rate": "66.6667",
    "icon_url": null,
    "active": true
  }
]
```

| Field | Meaning |
|---|---|
| `slug` | Used in URLs (`recharge.html?app=baat`) and to find the icon file `frontend/icons/<slug>.png` |
| `conversion_rate` | Coins per 1 KES (derived from the coin's price per 1,000) |
| `icon_url` | Uploaded icon, or `null`. The frontend falls back to `icons/<slug>.png` |

---

## POST /api/recharges/

Creates an order and initiates an STK Push.

**Request**

```json
{
  "coin_type_slug": "baat",
  "app_user_id": "1234567890",
  "phone_number": "254712345678",
  "coins_requested": 5000
}
```

| Field | Rules |
|---|---|
| `coin_type_slug` | Must match an **active** coin |
| `app_user_id` | 1 to 10 digits, numbers only |
| `phone_number` | Kenyan M-Pesa number. Common formats are normalised to `254XXXXXXXXX`. The website always sends the `254` form |
| `coins_requested` | Integer, at least 1000, and a multiple of 1000 |

**Response 201**

```json
{
  "reference": "CH2410260001",
  "amount_kes": 75,
  "message": "Payment initiated. Check your phone for the M-Pesa prompt."
}
```

`amount_kes` is a whole number of shillings (the exact price rounded up).

**Response 400** (validation), field names map to error lists:

```json
{
  "coins_requested": ["Coins must be bought in multiples of 1,000 (1,000, 2,000, 3,000…)."],
  "app_user_id": ["App User ID must be between 1 and 10 digits long and contain only numbers."]
}
```

**Response 500**: `{"error": "..."}` when the amount calculation or database save fails.

---

## GET /api/payment-status/<reference>/

Used by the website after the STK Push to find out what happened.

```json
{
  "reference": "CH2410260001",
  "coin_type_name": "Baat",
  "app_user_id": "1234567890",
  "coins_requested": 5000,
  "amount_paid": "75.00",
  "status": "paid",
  "payment_status": "success",
  "mpesa_receipt": "RGQ12345XY",
  "created_at": "2026-10-24T10:30:00Z"
}
```

| Order `status` | Meaning |
|---|---|
| `pending` | Waiting for the customer or for Safaricom |
| `paid` | Payment confirmed, waiting for staff to load coins |
| `loaded` | Staff have loaded the coins |
| `failed` | Payment failed or was cancelled |

| `payment_status` | Meaning |
|---|---|
| `pending`, `success`, `failed`, `cancelled` | State of the M-Pesa transaction |

Returns 404 for an unknown reference.

---

## POST /api/payments/daraja/callback/

Called by Safaricom's servers with the STK result. Do not call it from the website.

- Always answers `{"ResultCode": 0, "ResultDesc": "Accepted"}` so Safaricom does not keep retrying.
- Looks the payment up by `CheckoutRequestID` inside a database transaction with a row lock.
- Ignores unknown IDs, and ignores payments already marked `success` or `failed` (safe against retries).
- On `ResultCode` 0: stores the M-Pesa receipt, marks Payment `success` and Order `paid`.
- On any other code: marks Payment `failed` and Order `failed`.
- The full callback JSON is stored on the payment for audit.

The route is public by necessity. Its protection is discussed in [Security](security.md).

---

## Errors and rate limits

| Status | Meaning |
|---|---|
| 400 | Validation error (see field messages) |
| 404 | Unknown reference |
| 429 | Rate limit reached for this IP |
| 500 | Server error (check the logs) |
