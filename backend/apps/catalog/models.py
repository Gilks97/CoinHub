"""
CoinHub catalog — CoinType model.
"""
from decimal import Decimal, ROUND_CEILING

from django.core.validators import MinValueValidator
from django.db import models
from apps.core.models import TimestampedModel


class CoinType(TimestampedModel):
    """
    Represents one of the supported coin/game products.

    price_per_1000: what you edit in the admin (KES per 1,000 coins).
    conversion_rate: coins per 1 KES. It is calculated automatically from
    price_per_1000 every time a coin is saved. The payable amount is:
    CEIL(coins_requested / conversion_rate)
    """

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    # The price you actually think in. Edit this in the admin.
    price_per_1000 = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=15,
        validators=[MinValueValidator(Decimal("0.0001"))],
        help_text="KES per 1,000 coins, e.g. 15.4. The conversion rate is calculated from this.",
    )

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

    # NEW: keep conversion_rate in sync with price_per_1000 on every save.
    # Rounded UP (ROUND_CEILING) so an exact price such as 5,000 BoloUp = 77 KES
    # never turns into 78 because of a tiny rounding difference.
    def save(self, *args, **kwargs):
        self.conversion_rate = (Decimal(1000) / self.price_per_1000).quantize(
            Decimal("0.0001"), rounding=ROUND_CEILING
        )
        super().save(*args, **kwargs)

    def calculate_kes(self, coins: int) -> int:
        """Return the KES amount (rounded up) for the given coin quantity."""
        import math
        return math.ceil(coins / float(self.conversion_rate))