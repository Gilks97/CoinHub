# Getting started

Run CoinHub on your own computer.

## Prerequisites

- Git
- **Docker** with Compose v2, or **Podman** with `podman-compose`
- A text editor
- Optional for payments: a Safaricom Daraja developer account

The compose file contains `userns: keep-id` and `:Z` volume labels. These are for Podman on SELinux systems (such as Fedora) and are harmless on Docker.

## 1. Clone and configure

```bash
git clone https://github.com/**username**/CoinHub.git
cd CoinHub
cp .env.example .env
```

Edit `.env`. For local use the important values are:

```env
SECRET_KEY=any-long-random-string
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

DB_NAME=coinhub_db
DB_USER=coinhub_user
DB_PASSWORD=choose-a-simple-password

# The Django settings read ONLY DATABASE_URL. It must match the three DB_* values above.
# Host is "db" (the compose service name). sslmode=disable because the local container has no SSL.
DATABASE_URL=postgres://coinhub_user:choose-a-simple-password@db:5432/coinhub_db?sslmode=disable

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=you@example.com
DJANGO_SUPERUSER_PASSWORD=choose-a-strong-password
```

> **Important:** the `DB_*` variables configure the PostgreSQL container, while Django connects through `DATABASE_URL`. If the two disagree you get `password authentication failed`. Use a simple alphanumeric password locally; characters such as `@ # / : ?` must be URL-encoded inside `DATABASE_URL`.

The Daraja variables are only needed when you test payments. See [Configuration](configuration.md) and [Payments and Daraja](payments-daraja.md).

## 2. Build and start

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f web
```

On start the web container (see `docker/entrypoint.sh`):

1. waits for and checks the database (`check_db.py`),
2. applies migrations (which also seed and update the coin catalog),
3. collects static files,
4. creates the superuser from the `DJANGO_SUPERUSER_*` values (it prints "already taken" on later starts, which is harmless),
5. starts Gunicorn.

## 3. Open it

| URL | What |
|---|---|
| http://localhost:8080/ | Customer website |
| http://localhost:8080/admin/ | Admin panel (use your `DJANGO_SUPERUSER_*` login) |
| http://localhost:8080/api/coins/ | Coins API |

Default admin credentials (set in `.env`):
- **Username:** `admin`
- **Password:** `Admin@CoinHub2025!`

If the website loads but shows no coins, check `docker compose logs web` and see [Troubleshooting](troubleshooting.md).

## 4. Everyday commands

```bash
docker compose exec web python manage.py migrate          # apply migrations
docker compose exec web python manage.py showmigrations   # see what has been applied
docker compose exec web python manage.py shell            # Django shell
docker compose down                                       # stop (keeps the database)
docker compose down -v                                    # stop and DELETE the local database
```

Frontend files (`frontend/`) are mounted into Nginx, so edits show after a browser refresh. If a change does not appear, do a hard refresh (Ctrl+Shift+R) because browsers cache JavaScript.

## Running without containers

Requirements: Python 3.12, PostgreSQL 16.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/local.txt
```

Create a local database, set `DATABASE_URL` in `.env` (host `localhost`, `?sslmode=disable`), then:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Serve the frontend separately, for example `cd frontend && python -m http.server 8080`. Because the frontend is then on a different origin from Django, point `API_BASE` in `frontend/js/config.js` at `http://localhost:8000/api` and add `http://localhost:8080` to `CORS_ALLOWED_ORIGINS`.

## Receiving Daraja callbacks locally

Safaricom must reach your machine over public HTTPS. Use a tunnel such as ngrok, and set:

```env
DARAJA_CALLBACK_URL=https://<your-tunnel-id>.ngrok-free.app/api/payments/daraja/callback/
```

## Next steps

- [Architecture](architecture.md) for how the pieces fit together
- [Admin panel](admin-panel.md) to operate the system
- [Testing](testing.md) to run the browser tests
