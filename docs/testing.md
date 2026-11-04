# Testing

CoinHub is tested end to end with **Playwright** (a real browser driving the running site) and a short manual checklist. Automated backend unit tests are a future addition.

## Browser tests with Playwright

Tests live in `e2e/` (a separate Node project, so the Django project stays clean).

### One-time setup (Fedora example)

Playwright officially supports Debian and Ubuntu only, so on Fedora install the browser libraries with `dnf` and skip `--with-deps`:

```bash
sudo dnf install -y nodejs npm
cd e2e
npm install
npx playwright install chromium
sudo dnf install -y atk at-spi2-atk at-spi2-core cups-libs libXcomposite libXdamage \
  libXfixes libXrandr nss nspr alsa-lib pango cairo mesa-libgbm libxkbcommon libdrm
```

If Chromium still reports missing libraries, run `ldd ~/.cache/ms-playwright/chromium-*/chrome-linux/chrome | grep "not found"` and install what it lists. Use Chromium only (WebKit is unreliable on Fedora). On Ubuntu or Debian, `npx playwright install --with-deps chromium` works.

In VS Code, install the extension **Playwright Test for VSCode** to run and debug tests from the Testing sidebar.

### Running

Start the stack first (`docker compose up -d`), then from `e2e/`:

```bash
npx playwright test                 # headless, all projects
npx playwright test --ui            # interactive UI
npx playwright test --headed        # watch the browser
npx playwright show-report          # open the HTML report
npx playwright codegen http://localhost:8080   # record a new test
```

The admin test needs credentials of a **test** account on a **test** database:

```bash
ADMIN_USER=admin ADMIN_PASS=your-test-password npx playwright test
```

Never run tests against production data or with production credentials.

### What the tests cover

| Area | Checks |
|---|---|
| Recharge form | Phone formats `7XX`, `07XX` and `011` enable the Continue button; invalid amounts show the warning and disable it |
| Price preview | KES shown for a known amount (for example 5,000 Baat coins = 75) |
| Confirm screen | Shows the full `+254` number |
| Home page | One card per active coin (adjust the expected count when coins change) |
| Admin on a phone | The orders table fits the screen without sideways page scroll |

### Rules for payment tests

- Never trigger real STK pushes from automated tests.
- Mock the network with `page.route('**/api/recharges/', ...)` and `page.route('**/api/payment-status/*', ...)` to exercise the confirm, polling, success and failure screens.

## Manual QA checklist

Run through this before a release.

**Customer flow**
- [ ] Home page lists every active coin with its icon
- [ ] Recharge page opens for a coin (`recharge.html?app=<slug>`)
- [ ] User ID rejects letters and more than 10 digits
- [ ] Phone accepts `7XX...`, `07XX...`, `011...`
- [ ] Coins below 1,000 or not a multiple of 1,000 are blocked with a warning
- [ ] KES preview matches the expected price
- [ ] Confirm screen shows the right app, ID, phone, coins and total
- [ ] Sandbox payment: prompt arrives, success screen shows reference and receipt
- [ ] Cancelled prompt shows the failure screen
- [ ] Timeout message appears if nothing is confirmed

**Admin**
- [ ] Paid orders appear; **Ship Coins** marks one as Loaded with the right user and time
- [ ] Tapping an App User ID copies it
- [ ] Orders and Payments tables are readable on a phone
- [ ] Editing a coin price updates the rate and the website
- [ ] A non-superuser cannot delete coins

**Money**
- [ ] A small real payment reaches `paid` and the receipt matches the till statement

## Reporting a bug

Include: what you did, what you expected, what happened, the order reference (if any), the time, and a screenshot. Do not include full phone numbers or secrets in public issues.
