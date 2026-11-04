# Contributing

## Workflow

1. Create a branch from `main` (`feature/<short-name>` or `fix/<short-name>`).
2. Make a focused change.
3. Run the project locally and test it ([Testing](testing.md)).
4. Update the documentation if behaviour, settings or screens changed.
5. Open a pull request describing what changed and why, and how you tested it.

## Rules that protect production

- **Migrations:** commit them, never edit one that has already run, create them locally ([Database and migrations](database-and-migrations.md)).
- **Secrets:** never commit `.env`, keys, passkeys, passwords or database dumps. Use `.env.example` for placeholders only.
- **Money logic:** prices are always calculated on the server. Changes to pricing, the callback or order status need a second reviewer.
- **Customer data:** do not log full phone numbers or paste real customer data into issues, tests or docs.
- **Frontend and backend rules** that appear in both places (coin minimum and step) must be changed together.

## Code style

- Python: PEP 8, readable names, short functions, docstrings for views and models. Prefer the Django ORM and `Decimal` for money.
- JavaScript: plain modern JavaScript (no build step). Build page content with DOM APIs or `textContent` rather than `innerHTML` for API data.
- Keep admin customisation in `backend/apps/core/static/coinhub_admin.css` and `.js`.

## Commit messages

Short, in the imperative: `Add per-phone throttle`, `Fix coin count in admin list`. Mention the area when useful (`payments:`, `admin:`, `docs:`).

## Pull request checklist

- [ ] Works locally with a fresh `docker compose up -d --build`
- [ ] New or changed behaviour is covered by a test or the manual checklist
- [ ] Migrations included and `makemigrations --check` is clean
- [ ] No secrets, no customer data
- [ ] Docs updated (and the user guide, if screens or rules for customers or staff changed)
- [ ] Browser cache considered (script version bumped if needed)

## Updating the documentation

| Change | Update |
|---|---|
| Environment variable added or changed | [Configuration](configuration.md), `.env.example`, [Deployment](deployment.md) |
| Endpoint or validation rule changed | [API reference](api-reference.md) |
| Prices, coins, minimums | [Coin catalog](coin-catalog.md) |
| Admin behaviour or permissions | [Admin panel](admin-panel.md) |
| Payment behaviour | [Payments and Daraja](payments-daraja.md) |
| Anything customers or staff see | `docs/user-guide/build_user_guide.py`, then regenerate the PDF |
| A security gap fixed | [Security](security.md) (move it from the roadmap to "Implemented") |

## Getting help

Open an issue (without secrets or customer data) or contact the maintainer.
