# Configuration

CoinHub is configured through environment variables (read with `python-decouple`, from the environment or a `.env` file in the project root), plus a few constants in code.

**Never commit `.env`.** Only `.env.example` (placeholders only) belongs in Git.

## Environment variables

### Django

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key. Long, random, unique per environment | required |
| `DEBUG` | `True` for local development only. **Must be `False` in production** | `False` |
| `ALLOWED_HOSTS` | Comma-separated host names, for example `coinhub-uzzu.onrender.com` | `localhost` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated origins allowed to call the API, for example the frontend URL | `http://localhost:8080` |
| `PORT` | Port Gunicorn binds to (Render sets it) | `8000` |

When `DEBUG` is `False`, HTTPS redirection and secure cookies are enabled.

### Database

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | Connection URL used by Django, for example `postgres://user:pass@host:5432/dbname` | required |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Used by the **PostgreSQL container** in `docker-compose.yml`. Must match `DATABASE_URL` locally | `coinhub_db`, `coinhub_user`, required |
| `DB_HOST`, `DB_PORT`, `DB_SSLMODE` | Used only by `check_db.py` when `DATABASE_URL` is not set | `db`, `5432`, `require` |

Notes:

- Django reads **only** `DATABASE_URL`. The `DB_*` variables do not configure Django.
- `check_db.py` adds `sslmode=require` to `DATABASE_URL` if no `sslmode` is present. For a local container (no SSL) put `?sslmode=disable` in the URL.
- In `settings.py`, `ssl_require` is enabled when `DEBUG` is `False`.
- URL-encode special characters in the password (`@` becomes `%40`).

### Safaricom Daraja

| Variable | Description |
|---|---|
| `DARAJA_ENV` | `sandbox` or `production`. Selects the Daraja base URL |
| `DARAJA_CONSUMER_KEY`, `DARAJA_CONSUMER_SECRET` | From your Daraja app (must match `DARAJA_ENV`) |
| `DARAJA_SHORTCODE` | For a till: the **Store / Head Office number** used for the password and as `BusinessShortCode` |
| `DARAJA_TILL_NUMBER` | The till number, sent as `PartyB` |
| `DARAJA_PASSKEY` | Lipa Na M-Pesa Online passkey for that shortcode |
| `DARAJA_CALLBACK_URL` | Public HTTPS URL ending in `/api/payments/daraja/callback/` |

Sandbox values (shortcode `174379`) will not work against production and vice versa. See [Payments and Daraja](payments-daraja.md).

### Rate limiting

| Variable | Description | Default |
|---|---|---|
| `THROTTLE_ANON` | Requests per IP for anonymous callers (all public endpoints share this) | `100/day` |
| `THROTTLE_USER` | Requests for authenticated callers | `1000/day` |

Each payment uses up to about 21 requests (one to create it plus up to 20 status checks), so the default allows only a handful of payments per IP per day. Review it before going live. See [Security](security.md).

### Default superuser

| Variable | Description |
|---|---|
| `DJANGO_SUPERUSER_USERNAME` | Created on first start |
| `DJANGO_SUPERUSER_EMAIL` | |
| `DJANGO_SUPERUSER_PASSWORD` | **Use a strong, unique password. Never reuse the example value** |

## Constants in code

| Where | Name | Meaning |
|---|---|---|
| `backend/config/settings.py` | `COIN_MIN_PURCHASE` | Minimum coins per order (1000) |
| `backend/config/settings.py` | `COIN_PURCHASE_STEP` | Coins must be a multiple of this (1000) |
| `frontend/js/config.js` | `COIN_MIN`, `COIN_STEP` | Same rules, for the browser's instant feedback |
| `frontend/js/config.js` | `POLL_INTERVAL_MS`, `POLL_MAX_ATTEMPTS` | Status polling: every 3000 ms, up to 20 times |
| `frontend/js/config.js` | `API_BASE` | `/api` on localhost, otherwise the backend URL |
| `backend/config/settings.py` | `JAZZMIN_SETTINGS` | Admin look and feel, custom CSS and JS |

The backend values are the real rules. The frontend values only give faster feedback, so always change both together.

## Frontend API address

`frontend/js/config.js` contains the production backend URL. If the backend moves to a new address, edit it there and redeploy the frontend.
