# Coin catalog

How coins are priced, how to change prices, and how to add or remove coins.

## How pricing works

Each coin stores **Price per 1000** (KES for 1,000 coins). When a coin is saved, CoinHub derives the **conversion rate** (coins per 1 KES):

```
conversion_rate = 1000 / price_per_1000      (rounded UP to 4 decimals)
amount_kes      = ceil(coins / conversion_rate)   (whole shillings)
```

The rate is rounded up so an exact price (for example 5,000 coins at 15.4 per 1,000 = 77) never becomes 78 through a rounding artefact. The final amount is always rounded up to a whole shilling because **STK Push cannot charge fractions of a shilling**.

### Examples

| Price per 1,000 | Pays for 1,000 | for 5,000 | for 10,000 |
|---|---|---|---|
| 15 | 15 | 75 | 150 |
| 15.4 | 16 | 77 | 154 |
| 13.8 | 14 | 69 | 138 |
| 1.6 | 2 | 8 | 16 |
| 0.16 | 1 | 1 | 2 |
| 0.1075 | 1 | 1 | 2 |

For very low prices the rounding is large in relative terms: 1,000 coins at 0.1075 still costs the minimum of KES 1.

### Purchase rules

- Minimum **1,000** coins, and only multiples of **1,000** (1,000, 2,000, 3,000 and so on).
- Enforced by the API (`COIN_MIN_PURCHASE`, `COIN_PURCHASE_STEP` in `settings.py`) and mirrored in the browser (`COIN_MIN`, `COIN_STEP` in `frontend/js/config.js`).

### Current prices

Prices are data, and the **admin panel is the source of truth**. The migrations set the starting values:

| Coin | Slug | KES per 1,000 |
|---|---|---|
| Baat | `baat` | 15 |
| BoloUp | `boloup` | 15.4 |
| Boomlive | `boomlive` | 15 (placeholder, edit in the admin) |
| Crush Live | `crush` | 15 |
| Dess Party | `dessparty` | 1.6 |
| Dream Party | `dreamparty` | 1.6 |
| Glow | `glow` | 1.6 |
| Hala | `hala` | 15 |
| Mashi | `mashi` | 0.1075 |
| Minemo | `minemo` | 0.16 |
| Poppo | `poppo` | 13.8 |
| Taka | `taka` | 15 |
| Tello | `tello` | 1.6 |

Ximi, Suva, Mimoon and Gamet were removed by migration `0006`.

## Change a price (no code needed)

1. Admin, **Coin Types**.
2. Edit **Price per 1000** in the list row and click **Save** (or open the coin and edit it there).
3. The **Conversion rate** column updates itself. The website uses the new price immediately.

An admin edit changes only that database. A brand-new database starts with the migration values.

## Hide or delete a coin

| Goal | Action |
|---|---|
| Stop selling a coin but keep history | Untick **Active** (or use **Hide selected coins**). The coin disappears from the website and from `/api/coins/` |
| Remove it for good | Only a superuser can delete, and only if the coin has **no orders** (orders protect it) |
| Remove it from every database, including new ones | Add a migration (see below) |

## Add a new coin

1. **Icon first.** Save a square PNG (about 256 x 256, small file size) in `frontend/icons/` named exactly like the slug in lowercase, for example `frontend/icons/newcoin.png`.
2. **Create the coin.** Admin, **Coin Types**, Add. Set **Name**, **Slug** (lowercase, no spaces; it must match the icon file name), **Price per 1000**, and tick **Active**.
3. Commit and deploy the icon with the frontend.

The home page and the recharge page build themselves from the API, so no code changes are needed. If the icon file is missing, the card shows a letter placeholder.

Avoid relying on the admin icon upload: uploaded files go to the server's `media/` folder, which is wiped on redeploy unless a persistent disk is attached. Files in `frontend/icons/` are safe.

### Making a new coin permanent for new databases

A coin created in the admin exists only in that database. To make it part of every new database, add a data migration in `backend/apps/catalog/migrations/` (numbered after the latest one). Use `update_or_create` keyed on the slug, and set `price_per_1000` and `active`. Never edit a migration that has already run anywhere (see [Database and migrations](database-and-migrations.md)).

## Remove a coin in every environment

Add a new migration that deletes the coin if it has no orders and deactivates it otherwise (see `0006_remove_unwanted_coins.py` for the pattern).

## Pricing caveats

- Check that the cost of an M-Pesa transaction does not exceed your margin on very small orders.
- If you want a different minimum for cheap coins, that needs a per-coin minimum (not implemented). Today the minimum is global.
