# Database and migrations

## Engine

PostgreSQL. Locally it runs as a container (`postgres:16-alpine`) with a named volume `postgres_data`. In production Django connects to a hosted PostgreSQL through `DATABASE_URL`.

## Migration rules

1. **Always commit migration files.** They are the history of the schema and of seed data. Production needs them to update itself.
2. **Never edit a migration that has run anywhere** (your laptop, production, a teammate's machine). Django runs each migration once per database and ignores later edits, so databases silently drift apart. Always add a new migration.
3. **Create migrations on your own computer**, review them, test with `migrate`, then commit.
4. **Never delete migration files** to "start again".

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py makemigrations --check --dry-run   # expect: No changes detected
docker compose exec web python manage.py migrate
docker compose exec web python manage.py showmigrations
```

`makemigrations` compares your models with the existing migration files and writes only the difference. It does not touch the database; `migrate` applies.

> **Known issue:** `docker/entrypoint.sh` runs `makemigrations --noinput` on every start. This can create unreviewed migration files inside the container that vanish on the next deploy. Remove that line and keep only `migrate`.

## Fresh database vs existing database

`migrate` applies only what each database is missing:

- **New database:** runs every migration in order and ends with the same data as production.
- **Existing database:** runs only the new ones.

## Catalog migration history

| Migration | What it does |
|---|---|
| `0001_initial` | Creates `CoinType` |
| `0002_seed_coin_types` | Seeds the first coin set |
| `0003_update_rates_add_coins` | Updates rates, adds Glow, Minemo, Dess Party, Tello, Dream Party |
| `0004_restore_unlisted_coins` | Makes sure Boomlive, Ximi, Suva, Mimoon, Gamet exist (fixed a mismatch between local and production) |
| `0005_coin_price_per_1000` | Adds `price_per_1000`, fills it for every coin; unpriced coins get 15 |
| `0006_remove_unwanted_coins` | Removes Ximi, Suva, Mimoon, Gamet (deactivates any that already have orders) |

The other apps each have an initial migration (`core`, `accounts`, `orders`, `payments`).

## Data migrations

Use `RunPython` for data changes such as prices and seed coins. Keep them safe to run on any database:

- use `update_or_create` or filter-and-update, not blind inserts,
- supply a reverse function (`migrations.RunPython.noop` if it cannot be undone),
- depend on the migrations whose tables you touch (for example `("orders", "0001_initial")`).

If a migration both changes the schema and updates data, add the new column *before* the data step. Altering a table after updating its rows in one transaction can fail on PostgreSQL.

## Integrity rules in the models

| Rule | Why |
|---|---|
| `Order.coin_type` uses `PROTECT` | A coin with orders cannot be deleted |
| `Payment.order` is one-to-one with `CASCADE` | Deleting an order removes its payment (avoid deleting orders) |
| `Order.reference` is unique | Safe lookup by reference |

## Backups

Production data includes customer phone numbers and payment records. Make sure your database host takes regular backups, and test a restore at least once. Treat any dump file as sensitive and never commit it.

## Resetting a local database

```bash
docker compose down -v      # deletes the local database volume
docker compose up -d --build
```

This is only for local use.
