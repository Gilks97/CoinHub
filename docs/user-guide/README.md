# User guide (PDF)

`CoinHub-User-Guide.pdf` is the non-technical guide for **customers** (Part 1) and **staff who ship orders** (Part 2). It tells readers when to contact a technician and what information to give.

The PDF is generated from `build_user_guide.py` so it can be kept in step with the product.

## Before you share it

Open `build_user_guide.py` and fill in the **CONTACT DETAILS** block at the top (technician name, phone, email, support hours, website URL). Then regenerate the PDF.

## Regenerate

```bash
pip install reportlab
python docs/user-guide/build_user_guide.py
```

This writes `docs/user-guide/CoinHub-User-Guide.pdf`. Commit both the script and the PDF.

## When to regenerate

- The recharge screens or rules change (minimum coins, phone formats, the polling time)
- The admin workflow changes (for example the Ship Coins process)
- The technician's contact details change

Update the `VERSION` and `UPDATED` values at the top of the script each time.

## Audience split

| Part | Reader | Content |
|---|---|---|
| Part 1 | Customers | How to recharge, how prices work, what the screens mean, simple fixes, when to call the technician |
| Part 2 | Staff | Signing in, handling paid orders, Ship Coins, copying User IDs, price changes, rules, when to call the technician |

Technical detail belongs in the Markdown pages in `docs/`, not in the PDF.
