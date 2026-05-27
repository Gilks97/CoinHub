"""
CoinHub catalog — CoinType model.
"""
from django.db import models
from apps.core.models import TimestampedModel


class CoinType(TimestampedModel):
    """
    Represents one of the 12 supported coin/game products.

    conversion_rate: how many coins equal 1 KES.
    For example, if 1 KES buys 10 coins, set conversion_rate=10.
    The payable amount is: CEIL(coins_requested / conversion_rate)
    """

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    conversion_rate = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        help_text="Coins per 1 KES. E.g. 10.0000 means 1 KES = 10 coins.",
    )
    icon = models.ImageField(upload_to="catalog/icons/", blank=True, null=True)
    active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = "Coin Type"
        verbose_name_plural = "Coin Types"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def calculate_kes(self, coins: int) -> int:
        """Return the KES amount (rounded up) for the given coin quantity."""
        import math
        return math.ceil(coins / float(self.conversion_rate))
