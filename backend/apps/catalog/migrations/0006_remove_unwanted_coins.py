"""
Remove Ximi, Suva, Mimoon and Gamet.
- No orders for the coin -> deleted.
- Has orders -> kept but deactivated (orders protect it from deletion).
Safe to run on any database, including ones where they are already gone.
"""
from django.db import migrations

REMOVE = ["ximi", "suva", "mimoon", "gamet"]


def remove_coins(apps, schema_editor):
    CoinType = apps.get_model("catalog", "CoinType")
    Order = apps.get_model("orders", "Order")
    for coin in CoinType.objects.filter(slug__in=REMOVE):
        if Order.objects.filter(coin_type=coin).exists():
            coin.active = False
            coin.save(update_fields=["active"])
        else:
            coin.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0005_coin_price_per_1000"),
        ("orders", "0001_initial"),   # needed so the Order table exists when this runs
    ]

    operations = [migrations.RunPython(remove_coins, migrations.RunPython.noop)]