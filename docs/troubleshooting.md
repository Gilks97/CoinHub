# Troubleshooting

Find the symptom, check the likely cause, apply the fix. For payment problems see also [Payments and Daraja](payments-daraja.md).

## Starting the project

| Symptom | Likely cause | Fix |
|---|---|---|
| `password authentication failed for user "postgres"` (or any user) in the web logs | `DATABASE_URL` in `.env` does not match the `DB_*` values the database container was created with, or the Postgres volume remembers an older password | Make `DATABASE_URL` user, password and database match `DB_USER`, `DB_PASSWORD`, `DB_NAME`. If you changed them after the first start, run `docker compose down -v` (deletes local data) and start again |
| Same error with a password containing `@ # / :` | Special characters not URL-encoded in `DATABASE_URL` | URL-encode them (`@` is `%40`) or use a simple local password |
| `server does not support SSL` | `check_db.py` or `ssl_require` forces SSL against the local container | Add `?sslmode=disable` to the local `DATABASE_URL` and keep `DEBUG=True` locally |
| Web container exits right after starting | Database check failed | `docker compose logs -f web` and read the `[DB ERROR DETAILS]` line |
| `CommandError: That username is already taken` at startup | Superuser already exists | Harmless, nothing to fix |
| Static files warning "Found another file with the destination path" | Two apps ship the same admin file | Harmless |

## Website

| Symptom | Likely cause | Fix |
|---|---|---|
| Console error `getLocalPhone is not defined` (or an old behaviour persists) | Browser is running a cached old `recharge.js` | Hard refresh (Ctrl+Shift+R), tick "Disable cache" in DevTools Network, or bump the `?v=` on the script tags. Make sure the right site (local vs deployed) has the new files |
| Continue button stays disabled | A rule is not met, or JavaScript failed | Check User ID (1 to 10 digits), phone (`7XX`, `07XX`, `011`), coins (1,000 minimum, multiples of 1,000). Open the console (F12) for red errors |
| Fewer coins than expected on the site | Some coins are inactive or missing in **that** database | Compare **Coin Types** in the admin with `/api/coins/`. Local and production databases are separate; run migrations on both |
| A coin shows a letter instead of an icon | No `frontend/icons/<slug>.png`, or the file name does not match the slug (lowercase) | Add or rename the file and redeploy the frontend |
| Website cannot reach the API from the deployed frontend | `API_BASE` in `config.js` or `CORS_ALLOWED_ORIGINS` is wrong | Correct them and redeploy |
| First page load is very slow on Render | Free service waking up | Wait, or use an always-on plan |
| Error 429 | Anonymous rate limit reached for that IP | Wait, or raise `THROTTLE_ANON` (see [Configuration](configuration.md)) |

## Payments

| Symptom | Likely cause | Fix |
|---|---|---|
| Callback says "Merchant does not exist" | Till (`PartyB`) not linked to `BusinessShortCode`, till not enabled for STK, or sandbox and production values mixed | See the till section in [Payments and Daraja](payments-daraja.md) and contact Daraja support with the `CheckoutRequestID` |
| No STK prompt on the phone | Wrong number, phone unreachable, or request rejected | Check the payment's **Safaricom Handshake Response** in the admin |
| Order stays `pending` | Callback not received | Check `DARAJA_CALLBACK_URL` (public, HTTPS, correct path `/api/payments/daraja/callback/`) and the backend logs |
| Customer says they paid but the order is `failed` | Rare mismatch or lost callback | Compare the M-Pesa receipt with the till statement and escalate to the technician |
| Amount seems slightly higher than the listed price | Amounts round **up** to whole shillings | Expected. See [Coin catalog](coin-catalog.md) |

## Admin

| Symptom | Likely cause | Fix |
|---|---|---|
| Admin looks unstyled or tables are narrow on a phone | Custom CSS not collected or cached | Run collectstatic (the entrypoint does), hard refresh. Check that `custom_css` and `custom_js` in `JAZZMIN_SETTINGS` match the files in `backend/apps/core/static/` |
| Tap-to-copy does nothing | Cached JS, or the page is not HTTPS | Hard refresh. Copying uses the clipboard API which needs HTTPS (a fallback is included) |
| Cannot delete a coin | It has orders, or you are not a superuser | Hide it (untick **Active**) instead |
| Staff cannot see a section | Missing permission | Add the permission to their group |
| Coin price edit did not change the site | Edited the wrong database | Edit it in the environment you are looking at; admin edits are per database |

## Migrations

| Symptom | Likely cause | Fix |
|---|---|---|
| `makemigrations` creates an unexpected file | Model and migration state differ | Read the generated file; do not commit it blindly. Run `makemigrations --check --dry-run` |
| Different data in local and production | A migration was edited after it had already run somewhere | Add a new migration to correct it (see [Database and migrations](database-and-migrations.md)) |
| "Table already exists" on migrate | Database was created outside migrations | Use a fresh database, or fake the matching migration only if you are certain |

## Collecting information before asking for help

- The exact error text and the time it happened
- The order reference (for payment issues)
- `docker compose logs web` (or the Render logs) around that time
- What you changed last

Remove secrets and customer data before sharing anything.
