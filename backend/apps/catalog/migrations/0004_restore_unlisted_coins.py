"""Ensure the 5 coins not covered by 0003 exist everywhere, with tidy prices.
Price is KES per 1,000 coins. (Fixes local vs prod mismatch.)"""
from decimal import Decimal, ROUND_CEILING
from django.db import migrations

# (name, slug, KES per 1000 coins)  -- CONFIRM these; they are your old rates rounded to 2 decimals
PRICES = [
    ("Boomlive", "boomlive", "15.29"),
    ("Ximi",     "ximi",     "10.40"),
    ("Suva",     "suva",     "14.44"),
    ("Mimoon",   "mimoon",   "8.67"),
    ("Gamet",    "gamet",    "10.00"),
]

def restore(apps, schema_editor):
    CoinType = apps.get_model("catalog", "CoinType")
    for name, slug, price in PRICES:
        # same rule as 0003: coins-per-KES rounded UP to 4 decimals
        rate = (Decimal(1000) / Decimal(price)).quantize(Decimal("0.0001"), rounding=ROUND_CEILING)
        CoinType.objects.update_or_create(
            slug=slug,
            defaults={"name": name, "conversion_rate": rate, "active": True},
        )

class Migration(migrations.Migration):
    dependencies = [("catalog", "0003_update_rates_add_coins")]
    operations = [migrations.RunPython(restore, migrations.RunPython.noop)]