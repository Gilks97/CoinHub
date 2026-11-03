"""
Add CoinType.price_per_1000 (KES per 1,000 coins) and fill it for every coin.

- Coins with a price you specified keep that exact price.
- The 5 coins without a specified price (Boomlive, Ximi, Suva, Mimoon, Gamet)
  are set to KES 15 per 1,000. Change them later in the admin panel.
- conversion_rate is recalculated from the price (rounded UP to 4 decimals).
"""
import django.core.validators
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP
from django.db import migrations, models

PRICES = {
    "baat": "15", "boloup": "15.4", "crush": "15", "hala": "15",
    "mashi": "0.1075", "poppo": "13.8", "taka": "15",
    "glow": "1.6", "minemo": "0.16", "dessparty": "1.6",
    "tello": "1.6", "dreamparty": "1.6",
    "boomlive": "13.58", "ximi": "15", "suva": "15", "mimoon": "15", "gamet": "15",
}


def backfill_prices(apps, schema_editor):
    CoinType = apps.get_model("catalog", "CoinType")
    for coin in CoinType.objects.all():
        if coin.slug in PRICES:
            price = Decimal(PRICES[coin.slug])
        else:
            # any other coin added by hand: derive its price from the current rate
            price = (Decimal(1000) / coin.conversion_rate).quantize(
                Decimal("0.0001"), rounding=ROUND_HALF_UP
            )
        coin.price_per_1000 = price
        coin.conversion_rate = (Decimal(1000) / price).quantize(
            Decimal("0.0001"), rounding=ROUND_CEILING
        )
        coin.save(update_fields=["price_per_1000", "conversion_rate"])


class Migration(migrations.Migration):

    dependencies = [("catalog", "0004_restore_unlisted_coins")]

    operations = [
        migrations.AddField(
            model_name="cointype",
            name="price_per_1000",
            field=models.DecimalField(
                decimal_places=4,
                default=15,
                help_text="KES per 1,000 coins, e.g. 15.4. The conversion rate is calculated from this.",
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(Decimal("0.0001"))],
            ),
        ),
        migrations.RunPython(backfill_prices, migrations.RunPython.noop),
    ]