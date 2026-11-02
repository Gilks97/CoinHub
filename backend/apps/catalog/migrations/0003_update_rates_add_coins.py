"""Update coin prices and add new coins. Price is KES per 1,000 coins."""
from decimal import Decimal, ROUND_CEILING
from django.db import migrations

# (name, slug, KES per 1000 coins)
PRICES = [
    ("Baat",        "baat",       "15"),
    ("BoloUp",      "boloup",     "15.4"),
    ("Crush Live",  "crush",      "15"),
    ("Hala",        "hala",       "15"),
    ("Mashi",       "mashi",      "0.1075"),
    ("Poppo",       "poppo",      "13.8"),
    ("Taka",        "taka",       "15"),
    # NEW coins
    ("Glow",        "glow",       "1.6"),
    ("Minemo",      "minemo",     "0.16"), 
    ("Dess Party",  "dessparty",  "1.6"),
    ("Tello",       "tello",      "1.6"),
    ("Dream Party", "dreamparty", "1.6"),
]

def apply_prices(apps, schema_editor):
    CoinType = apps.get_model("catalog", "CoinType")
    for name, slug, price in PRICES:
        # conversion_rate = coins per 1 KES. Rounded UP (ROUND_CEILING) so an exact
        # price (e.g. 5,000 BoloUp = 77) never gets an accidental extra shilling.
        rate = (Decimal(1000) / Decimal(price)).quantize(Decimal("0.0001"), rounding=ROUND_CEILING)
        CoinType.objects.update_or_create(
            slug=slug,
            defaults={"name": name, "conversion_rate": rate, "active": True},
        )

class Migration(migrations.Migration):
    dependencies = [("catalog", "0002_seed_coin_types")]
    operations = [migrations.RunPython(apply_prices, migrations.RunPython.noop)]