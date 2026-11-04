# CoinHub

> Instant coin recharge platform for in-app coins, paid through M-Pesa (Safaricom Daraja STK Push).

Customers pick an app, enter their **App User ID**, their **M-Pesa number** and the **number of coins**. CoinHub calculates the price on the server, sends an STK Push prompt to the customer's phone, and tracks the payment until Safaricom confirms it. A staff member then loads the coins manually and marks the order as loaded in the admin panel.

No customer registration is required.

---

## At a glance

| | |
|---|---|
| **Backend** | Django 5, Django REST Framework, Gunicorn, WhiteNoise |
| **Database** | PostgreSQL (local container, or a hosted database such as Neon via `DATABASE_URL`) |
| **Admin UI** | Django admin themed with Jazzmin |
| **Payments** | Safaricom Daraja, M-Pesa Express (STK Push), Buy Goods (till) |
| **Frontend** | Static HTML, CSS and vanilla JavaScript (no build step) |
| **Containers** | Docker or Podman Compose (PostgreSQL, Django, Nginx) |
| **Hosting (current)** | Render (backend web service and static frontend) |

## Documentation

All technical documentation lives in [`docs/`](docs/README.md). Start there.

| I want to... | Read |
|---|---|
| Run the project on my computer | [Getting started](docs/getting-started.md) |
| Understand how the pieces fit together | [Architecture](docs/architecture.md) |
| Configure environment variables | [Configuration](docs/configuration.md) |
| Call or extend the API | [API reference](docs/api-reference.md) |
| Understand or debug M-Pesa payments | [Payments and Daraja](docs/payments-daraja.md) |
| Operate the admin panel | [Admin panel](docs/admin-panel.md) |
| Change coin prices, add or remove coins | [Coin catalog](docs/coin-catalog.md) |
| Work with migrations safely | [Database and migrations](docs/database-and-migrations.md) |
| Deploy or go live | [Deployment](docs/deployment.md) |
| Review security and the hardening roadmap | [Security](docs/security.md) |
| Test the system | [Testing](docs/testing.md) |
| Fix a problem | [Troubleshooting](docs/troubleshooting.md) |
| Contribute code | [Contributing](docs/contributing.md) |
| Hand a guide to customers or staff | [User guide (PDF)](docs/user-guide/CoinHub-User-Guide.pdf) |

## Quick start

```bash
git clone https://github.com/Gilks97/CoinHub.git
cd CoinHub
cp .env.example .env        # then edit the values (see docs/configuration.md)
docker compose up -d --build
```

Then open:

| URL | What |
|---|---|
| http://localhost:8080/ | Customer website |
| http://localhost:8080/admin/ | Admin panel |
| http://localhost:8080/api/coins/ | Coins API (JSON) |

Full instructions, including Podman and running without containers, are in [Getting started](docs/getting-started.md).

## Repository layout

```
CoinHub/
├── backend/                 Django project
│   ├── config/              settings, URL routing, custom admin site
│   └── apps/
│       ├── core/            base models, constants, utilities, admin CSS/JS
│       ├── catalog/         CoinType model, pricing, GET /api/coins/
│       ├── orders/          Order model, POST /api/recharges/, status endpoint
│       ├── payments/        Payment model, Daraja client, callback handler
│       └── accounts/        StaffProfile (role label for staff users)
├── frontend/                static site (index.html, recharge.html, js/, css/, icons/)
├── docker/                  entrypoint.sh and nginx.conf
├── docs/                    technical documentation and the user guide
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Project status

CoinHub is in active development and handles real payments. Before relying on it in production, read the [Security](docs/security.md) page, especially the **Known gaps and hardening roadmap** section.

## Support

For technical problems, contact the project maintainer (see the contact box in the user guide). Report bugs as GitHub issues, but **never post secrets, phone numbers, M-Pesa receipts or customer data in a public issue**.
