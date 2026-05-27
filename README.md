# CoinHub

> **Instant coin recharge platform powered by M-Pesa (Safaricom Daraja STK Push)**

CoinHub lets users top up their in-app coin balances across 12 supported apps — no registration required. Users select an app, enter their App User ID, M-Pesa number, and coin quantity. The platform calculates the KES amount server-side, initiates an STK Push, and tracks the payment through to confirmation.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start (Docker)](#quick-start-docker)
- [Local Development (without Docker)](#local-development-without-docker)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Admin Panel](#admin-panel)
- [Daraja Integration](#daraja-integration)
- [Supported Apps](#supported-apps)
- [Security](#security)
- [Deployment](#deployment)

---

## Architecture Overview

```
Browser (Frontend)
       │
       ▼
  Nginx (port 80)
  ├── /          → serves frontend/ static files
  ├── /api/      → proxies to Django/Gunicorn
  ├── /admin/    → proxies to Django/Gunicorn
  └── /static/   → serves Django collected static
       │
       ▼
  Django 5 + DRF (port 8000 internal)
  ├── apps/catalog    — CoinType model + rates API
  ├── apps/orders     — Order creation + status polling
  ├── apps/payments   — Payment tracking + Daraja callback
  ├── apps/accounts   — Staff profiles + roles
  └── apps/core       — Base models, utils, reference gen
       │
       ▼
  PostgreSQL 16
```

**Payment flow:**

1. User fills form → `POST /api/recharges/`
2. Backend calculates KES server-side (never from client)
3. Backend creates `Order` + `Payment` records
4. Backend calls Daraja STK Push to customer's phone
5. Customer enters M-Pesa PIN
6. Safaricom calls `POST /api/payments/callback/`
7. Backend marks Order → `paid`, Payment → `success`
8. Frontend polls `GET /api/payment-status/<ref>/` until confirmed
9. Admin manually loads coins and marks Order → `loaded`

---

## Tech Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Backend      | Django 5, Django REST Framework     |
| Database     | PostgreSQL 16                       |
| Admin UI     | Jazzmin                             |
| Payment      | Safaricom Daraja (STK Push)         |
| Frontend     | Vanilla JS, CSS custom properties   |
| Fonts        | Syne (display), DM Sans (body)      |
| Serving      | Gunicorn + Nginx                    |
| Containers   | Docker + Docker Compose             |

---

## Project Structure

```
CoinHub/
├── frontend/
│   ├── index.html          # App selection page
│   ├── recharge.html       # Recharge form + payment flow
│   ├── css/
│   │   └── style.css       # All styles (dark-gold design system)
│   ├── js/
│   │   ├── config.js       # API base URL + constants
│   │   ├── api.js          # Fetch-based API client
│   │   ├── index.js        # App grid rendering
│   │   └── recharge.js     # Multi-step form + polling
│   └── icons/              # App icons (hala.png, boloup.png …)
│
├── backend/
│   ├── manage.py
│   ├── config/
│   │   ├── settings.py     # All Django settings
│   │   ├── urls.py         # Root URL conf
│   │   ├── api_urls.py     # /api/* routes
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── core/           # Base models, utils, constants, mgmt commands
│   │   ├── accounts/       # StaffProfile (SuperAdmin / Agent roles)
│   │   ├── catalog/        # CoinType model + GET /api/coins/
│   │   ├── orders/         # Order model + POST /api/recharges/ + status
│   │   └── payments/       # Payment model + Daraja integration + callback
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── local.txt
│   │   └── production.txt
│   └── static/             # Custom static assets (empty by default)
│
├── docker/
│   ├── entrypoint.sh       # Migrate → collectstatic → create superuser → gunicorn
│   └── nginx.conf          # Nginx reverse proxy + frontend serving
│
├── Dockerfile
├── docker-compose.yml
├── .env                    # Local dev env vars (not committed)
├── .env.example            # Template — commit this
├── .gitignore
└── README.md
```

---

## Quick Start (Docker)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/) v2

### 1. Clone and configure

```bash
git clone <your-repo-url> CoinHub
cd CoinHub

# Copy and edit the env file
cp .env.example .env
nano .env          # Fill in your Daraja credentials
```

### 2. Build and start

```bash
docker compose up --build
```

This will:
- Start PostgreSQL
- Run all Django migrations
- Seed the 12 coin types
- Collect static files
- Create the default superuser
- Start Gunicorn + Nginx

### 3. Access

| URL                          | What                        |
|------------------------------|-----------------------------|
| http://localhost/            | CoinHub frontend            |
| http://localhost/admin/      | Jazzmin admin panel         |
| http://localhost/api/coins/  | Coins API (JSON)            |

Default admin credentials (set in `.env`):
- **Username:** `admin`
- **Password:** `Admin@CoinHub2025!`

---

## Local Development (without Docker)

### Prerequisites

- Python 3.12+
- PostgreSQL 16 running locally
- pip

### Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate

# Install deps
pip install -r requirements/local.txt

# Set environment variables
# Edit .env in project root — then export them, or use direnv/python-decouple
# (python-decouple reads .env automatically from the project root)

# Run migrations
python manage.py migrate

# Seed superuser
python manage.py create_default_superuser

# Start dev server
python manage.py runserver
```

For the frontend in development, open `frontend/index.html` directly in a browser,
or use a simple static server:

```bash
cd frontend
python -m http.server 8080
```

> **Note:** update `CONFIG.API_BASE` in `js/config.js` to `http://localhost:8000/api`
> when running the frontend separately from Django.

---

## Environment Variables

| Variable                     | Description                                      | Default          |
|------------------------------|--------------------------------------------------|------------------|
| `SECRET_KEY`                 | Django secret key                                | *(required)*     |
| `DEBUG`                      | Debug mode (`True`/`False`)                      | `False`          |
| `ALLOWED_HOSTS`              | Comma-separated allowed hostnames                | `localhost`      |
| `DB_NAME`                    | PostgreSQL database name                         | `coinhub_db`     |
| `DB_USER`                    | PostgreSQL user                                  | `coinhub_user`   |
| `DB_PASSWORD`                | PostgreSQL password                              | *(required)*     |
| `DB_HOST`                    | PostgreSQL host                                  | `db`             |
| `DB_PORT`                    | PostgreSQL port                                  | `5432`           |
| `DARAJA_CONSUMER_KEY`        | Daraja app consumer key                          | *(required)*     |
| `DARAJA_CONSUMER_SECRET`     | Daraja app consumer secret                       | *(required)*     |
| `DARAJA_SHORTCODE`           | M-Pesa shortcode (paybill/till)                  | *(required)*     |
| `DARAJA_TILL_NUMBER`         | Till number for CustomerBuyGoods                 | *(required)*     |
| `DARAJA_PASSKEY`             | Lipa Na M-Pesa passkey                           | *(required)*     |
| `DARAJA_CALLBACK_URL`        | Public HTTPS URL Safaricom posts callbacks to    | *(required)*     |
| `DARAJA_ENV`                 | `sandbox` or `production`                        | `sandbox`        |
| `CORS_ALLOWED_ORIGINS`       | Comma-separated allowed origins for CORS         | `http://localhost:8080` |
| `THROTTLE_ANON`              | DRF anon throttle rate                           | `100/day`        |
| `THROTTLE_USER`              | DRF user throttle rate                           | `1000/day`       |
| `DJANGO_SUPERUSER_USERNAME`  | Default superuser username                       | `admin`          |
| `DJANGO_SUPERUSER_EMAIL`     | Default superuser email                          | *(see .env)*     |
| `DJANGO_SUPERUSER_PASSWORD`  | Default superuser password                       | *(see .env)*     |

---

## API Reference

### `GET /api/coins/`

Returns all active coin types.

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "name": "Hala",
    "slug": "hala",
    "conversion_rate": "66.6667",
    "icon_url": "http://localhost/media/catalog/icons/hala.png",
    "active": true
  }
]
```

---

### `POST /api/recharges/`

Create an order and initiate M-Pesa STK Push.

**Request body:**
```json
{
  "coin_type_slug":  "hala",
  "app_user_id":    "USER12345",
  "phone_number":   "254712345678",
  "coins_requested": 1000
}
```

**Response `201 Created`:**
```json
{
  "reference":  "CH2605250001",
  "amount_kes": 15,
  "message":    "Payment initiated. Check your phone for the M-Pesa prompt."
}
```

**Errors `400 Bad Request`:**
```json
{
  "coin_type_slug": ["Coin type not found or inactive."],
  "phone_number":   ["Enter a valid Kenyan M-Pesa number."]
}
```

---

### `GET /api/payment-status/<reference>/`

Poll for payment status after initiating a recharge.

**Response `200 OK`:**
```json
{
  "reference":      "CH2605250001",
  "coin_type_name": "Hala",
  "app_user_id":    "USER12345",
  "coins_requested": 1000,
  "amount_paid":    "15.00",
  "status":         "paid",
  "payment_status": "success",
  "mpesa_receipt":  "RGQ12345XY",
  "created_at":     "2025-05-26T10:30:00Z"
}
```

**Order statuses:** `pending` → `paid` → `loaded` (or `failed`)
**Payment statuses:** `pending` → `success` (or `failed` / `cancelled`)

---

### `POST /api/payments/callback/`

Daraja STK Push result callback — called by **Safaricom servers only**.
No authentication required (IP allowlisting recommended in production).

**Always responds:**
```json
{ "ResultCode": 0, "ResultDesc": "Accepted" }
```

---

## Admin Panel

Access at `/admin/` with superuser credentials.

**Jazzmin dashboard sections:**

| Section   | Features                                            |
|-----------|-----------------------------------------------------|
| Coins     | Manage CoinType, set conversion rates, upload icons |
| Orders    | View all orders, filter by status/app, mark loaded  |
| Payments  | Full payment audit trail including raw Daraja JSON  |
| Users     | Manage admin users and Staff Profiles               |

**Roles:**

- **SuperAdmin** — full CRUD, rate management, user management, mark orders as loaded
- **Agent** — read-only access to orders and payments

---

## Daraja Integration

CoinHub uses **Lipa Na M-Pesa Online (STK Push)** with transaction type `CustomerBuyGoodsOnline`.

**Setup steps:**

1. Create an app on [Safaricom Developer Portal](https://developer.safaricom.co.ke/)
2. Enable the **Lipa Na M-Pesa Online** API
3. Set your consumer key/secret in `.env`
4. For production, set `DARAJA_ENV=production`
5. Your `DARAJA_CALLBACK_URL` **must** be a publicly reachable HTTPS URL

**Local callback testing** (for development):
Use [ngrok](https://ngrok.com/) to expose your local server:
```bash
ngrok http 80
# Then set DARAJA_CALLBACK_URL=https://<ngrok-id>.ngrok.io/api/payments/callback/
```

---

## Supported Apps

| App         | Slug        |
|-------------|-------------|
| Hala        | `hala`      |
| BoloUp      | `boloup`    |
| Poppo       | `poppo`     |
| Baat        | `baat`      |
| Taka        | `taka`      |
| Mashi       | `mashi`     |
| Crush Live  | `crush`     |
| Boomlive    | `boomlive`  |
| Ximi        | `ximi`      |
| Suva        | `suva`      |
| Mimoon      | `mimoon`    |
| Gamet       | `gamet`     |

Conversion rates are stored in PostgreSQL and editable via the admin panel — no code changes needed.

---

## Security

- **Server-side-only** coin → KES calculation. Client sends coin quantity; amount is never trusted from the frontend.
- **CSRF protection** on all Django views (disabled only on the Daraja callback endpoint which uses no session).
- **DRF throttling** on all public endpoints (configurable via env vars).
- **Environment variables** for all secrets — never hardcoded.
- **PostgreSQL** with a dedicated, least-privilege user.
- **Non-root Docker user** (`appuser`) inside the container.
- All raw Daraja callback payloads stored in `Payment.raw_callback_json` for audit.

---

## Deployment

### Production checklist

- [ ] Set `DEBUG=False`
- [ ] Set a strong random `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` to your domain(s)
- [ ] Set `DARAJA_ENV=production`
- [ ] Set `DARAJA_CALLBACK_URL` to a public HTTPS URL
- [ ] Point `CORS_ALLOWED_ORIGINS` to your frontend domain
- [ ] Configure SSL termination (Nginx or load balancer)
- [ ] Restrict `/api/payments/callback/` to Safaricom IP ranges
- [ ] Set up database backups for the PostgreSQL volume

### One-command production deploy

```bash
docker compose up -d --build
```

---

## License

 © 2025 CoinHub
