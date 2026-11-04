# Admin panel

The admin panel is Django's admin with the Jazzmin theme, available at `/admin/`.

## Signing in

Use the username and password of a staff account. The first superuser is created from the `DJANGO_SUPERUSER_*` environment variables (see [Configuration](configuration.md)). Only users with **Staff status** can sign in.

## Dashboard

The home page shows summary cards (orders today, paid today, pending today, revenue today, revenue this month) followed by the model sections.

## Sections

| Section | What it is for |
|---|---|
| **Orders** | Every recharge request. Search, filter, ship coins |
| **Payments** | Read-only M-Pesa audit trail, including the raw Daraja payloads |
| **Coin Types** | Prices, visibility and details of each coin |
| **Staff Profiles** | A role label attached to staff users |
| **Users / Groups** | Staff accounts and permission groups |

## Handling orders (daily workflow)

1. Open **Orders** and filter by **Status = Paid**. These are customers who have paid and are waiting for coins.
2. For each order, note the **App User ID**, **coin type** and **coins requested**. Tap an App User ID to copy it.
3. Load the coins in the external app (this happens outside CoinHub).
4. Press the green **Ship Coins** button on that row. CoinHub records the time and the staff member, and the status becomes **Loaded**.
5. For many orders at once, tick them and choose **Mark selected orders as Manually Loaded** from the Action dropdown.

| Status | Badge | Meaning |
|---|---|---|
| Pending | orange | Customer has not completed payment yet |
| Paid | green | Money received. Coins must be loaded |
| Loaded | blue | Coins loaded and recorded |
| Failed | red | Payment did not go through. No coins to load |

Useful search terms: order reference, App User ID, phone number. Filters: status, coin type, date.

> Only press **Ship Coins** after the coins are actually loaded. The button changes the record immediately and the customer's status page shows it.

## Payments

Payments are read-only. Open one to see the M-Pesa receipt, result code and description, and (in the collapsed **Raw API Payloads** section) exactly what was sent to and received from Safaricom. This is the main tool for diagnosing payment problems.

## Mobile use

The admin tables are widened on phones and scroll sideways inside their own box, so every column stays readable. The **App User ID** column is tappable: one tap copies the ID and shows a short "Copied" message. Long-pressing selects the whole ID and offers the phone's own Copy menu. The behaviour lives in `backend/apps/core/static/coinhub_admin.js` and `coinhub_admin.css`.

## Roles and permissions

CoinHub uses Django's standard users, groups and permissions as the real access control.

| Role | How it is set up |
|---|---|
| **SuperAdmin** | A user with **Superuser status** ticked. Can do everything, including deleting coins |
| **Admin** (recommended group) | Group with view/add/change on orders, payments (view only) and coins. **No delete permissions** |
| **Staff** (recommended group) | Group with view on orders and payments, plus change on orders (needed for Ship Coins). No delete permissions |

Every non-superuser also needs **Staff status** ticked to enter the admin. Create groups under **Groups**, then assign users to them.

### The StaffProfile role

`StaffProfile` has two labels, **SuperAdmin** and **Agent**. At present the only thing it changes is that an **Agent** sees all order fields as read-only. It does **not** grant or remove permissions on its own, and it does not stop an Agent from pressing Ship Coins. Rely on groups and permissions for access control, and treat the profile as an informational label.

### Deleting

| Item | Rule |
|---|---|
| Coin types | Only superusers can delete (enforced in `catalog/admin.py`). A coin that has orders cannot be deleted at all; hide it instead |
| Orders, payments | Deletion depends on Django permissions. Do not grant `delete` on these to anyone but a superuser; they are financial records |
| Users, groups | Deletion depends on Django permissions. See the hardening roadmap in [Security](security.md) for the recommended superuser-only rule |

## Common tasks

| Task | Where |
|---|---|
| Change a coin price | **Coin Types**, edit **Price per 1000** in the list, Save. See [Coin catalog](coin-catalog.md) |
| Hide a coin from the website | **Coin Types**, untick **Active**, or use the **Hide selected coins** action |
| Add a staff member | **Users**, Add user, tick **Staff status**, assign a group |
| Remove access | **Users**, untick **Active** (preferred to deleting) |
| Check a customer's payment | **Payments**, search by order reference, phone or M-Pesa receipt |

## Good practice

- Everyone gets their own account. Never share logins.
- Deactivate users instead of deleting them, so "loaded by" history stays meaningful.
- Sign out on shared devices.
- Use a strong password. A second factor for the admin is on the roadmap.
