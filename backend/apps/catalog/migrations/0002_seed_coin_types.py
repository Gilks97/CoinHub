"""
Seed migration: populate the 12 default CoinType entries.

Conversion rates derived from the original frontend appData:
  KES = CEIL( coins / rate )     (rate = coins per 1 KES approx)

Original JS used:  totalKes = CEIL( coins / appRate * 130 )
So: KES per coin = 130 / appRate
Stored as conversion_rate = appRate / 130  (coins per 1 KES)

We store conversion_rate as coins-per-KES so:
  amount_kes = CEIL(coins_requested / conversion_rate)
"""
from django.db import migrations


COIN_TYPES = [
    # (name, slug, conversion_rate)
    # rate from JS: appRate coins = 1 USD = 130 KES → coins_per_kes = appRate/130
    ("Hala",        "hala",      round((1040000 / 120) / 130, 4)),   # ≈ 66.6667
    ("BoloUp",      "boloup",    round(11000 / 130, 4)),              # ≈ 84.6154
    ("Poppo",       "poppo",     round(11500 / 130, 4)),              # ≈ 88.4615
    ("Baat",        "baat",      round(7000  / 130, 4)),              # ≈ 53.8462
    ("Taka",        "taka",      round(10000 / 130, 4)),              # ≈ 76.9231
    ("Mashi",       "mashi",     round(120000/ 130, 4)),              # ≈ 923.0769
    ("Crush Live",  "crush",     round(5000  / 130, 4)),              # ≈ 38.4615
    ("Boomlive",    "boomlive",  round(8500  / 130, 4)),              # ≈ 65.3846
    ("Ximi",        "ximi",      round(12500 / 130, 4)),              # ≈ 96.1538
    ("Suva",        "suva",      round(9000  / 130, 4)),              # ≈ 69.2308
    ("Mimoon",      "mimoon",    round(15000 / 130, 4)),              # ≈ 115.3846
    ("Gamet",       "gamet",     round(13000 / 130, 4)),              # ≈ 100.0000
]


def seed_coin_types(apps, schema_editor):
    CoinType = apps.get_model("catalog", "CoinType")
    for name, slug, rate in COIN_TYPES:
        CoinType.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "conversion_rate": rate, "active": True},
        )


def unseed_coin_types(apps, schema_editor):
    CoinType = apps.get_model("catalog", "CoinType")
    slugs = [s for _, s, _ in COIN_TYPES]
    CoinType.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_coin_types, reverse_code=unseed_coin_types),
    ]
