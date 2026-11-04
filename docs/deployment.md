# Deployment

CoinHub currently runs on **Render** as two services plus a hosted PostgreSQL database:

| Piece | Where | Notes |
|---|---|---|
| Backend (Django API and admin) | Render web service, built from the `Dockerfile` | Public URL, for example `https://coinhub-uzzu.onrender.com` |
| Frontend | Render static site, publishing the `frontend/` folder | Public URL, for example `https://coinhub-kjam.onrender.com` |
| Database | Hosted PostgreSQL (for example Neon) | Connected with `DATABASE_URL` and SSL |

Confirm the exact service settings (branch, build, publish directory) in your Render dashboard. They are not stored in this repository.

## Backend service

The container starts `docker/entrypoint.sh`, which:

1. checks the database connection,
2. runs migrations,
3. collects static files,
4. attempts to create the superuser,
5. starts Gunicorn on `$PORT` (3 workers, 120 s timeout).

### Environment variables (production)

Set these in the Render dashboard, never in the repository:

| Variable | Production value |
|---|---|
| `SECRET_KEY` | New long random value |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | The backend host name |
| `CORS_ALLOWED_ORIGINS` | The frontend URL (with `https://`) |
| `DATABASE_URL` | The hosted database URL (SSL on) |
| `DARAJA_ENV` | `production` |
| `DARAJA_CONSUMER_KEY`, `DARAJA_CONSUMER_SECRET` | Production Daraja app credentials |
| `DARAJA_SHORTCODE`, `DARAJA_TILL_NUMBER`, `DARAJA_PASSKEY` | Production values for your till |
| `DARAJA_CALLBACK_URL` | `https://<backend-host>/api/payments/daraja/callback/` |
| `DJANGO_SUPERUSER_*` | Real admin account with a strong, unique password |
| `THROTTLE_ANON`, `THROTTLE_USER` | Rates suited to real traffic |

With `DEBUG=False`, Django redirects HTTP to HTTPS and marks cookies secure. See [Configuration](configuration.md) for every variable.

## Frontend service

A static site with the **publish directory** set to `frontend`. There is no build step. `frontend/js/config.js` must contain the backend's public URL in `API_BASE` (used when the page is not on localhost).

Browsers cache JavaScript aggressively. After a change that must reach everyone immediately, bump the version in the script tags (for example `js/recharge.js?v=3`).

## Deploying a change

1. Merge to the branch Render watches (normally `main`).
2. Render rebuilds and redeploys. Migrations run automatically on backend start.
3. Check the backend logs for `Running migrations` and no errors.
4. Smoke test: `/api/coins/` returns the expected coins, the recharge page loads, the admin loads.

**Backend first, then frontend** when a change touches both, so the API accepts what the new page sends.

## Going live checklist

- [ ] `DEBUG=False`, new `SECRET_KEY`, correct `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`
- [ ] Production Daraja credentials, till and passkey, with `DARAJA_ENV=production`
- [ ] Callback URL is public HTTPS and points to the production backend
- [ ] A successful small real payment, end to end, with the order reaching `paid`
- [ ] Superuser password is strong and not the example value
- [ ] Database backups enabled and a restore tested
- [ ] Rate limits reviewed ([Configuration](configuration.md))
- [ ] Items on the [Security](security.md) roadmap marked critical are done
- [ ] Coin prices checked in the admin
- [ ] `docs/user-guide/CoinHub-User-Guide.pdf` filled in with technician contact details

## Free-tier behaviour (Render)

Free web services sleep after a period of inactivity, so the first request can be slow. A payment callback arriving while the service is asleep may be delayed, and a sleeping backend can cause a timeout on the customer's screen. For real traffic use an always-on plan.

## Uploaded media

Files uploaded through the admin are stored on the container's disk and are lost on redeploy unless a persistent disk is attached. Keep coin icons in `frontend/icons/` instead.

## Rolling back

Redeploy the previous commit from Render. Migrations are not automatically reversed, so avoid destructive migrations, and take a database backup before risky changes.

## Switching to a new database

1. Create the new database and set the new `DATABASE_URL`.
2. Deploy. All migrations run from `0001`, creating the schema and the coin catalog.
3. The superuser step creates the first admin from `DJANGO_SUPERUSER_*`.
4. Recreate staff users and groups, and review coin prices in the admin.

Orders and payments from the old database are not copied automatically.
