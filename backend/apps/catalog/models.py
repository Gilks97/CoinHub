"""
CoinHub catalog — CoinType model.
"""
from decimal import Decimal, ROUND_CEILING
from fractions import Fraction

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from apps.core.models import TimestampedModel


#Largest pack (in coins) we accept. Stops prices like 15.3333 that would need a huge pack.
MAX_PACK_COINS = 1_000_000
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

    # keep conversion_rate in sync with price_per_1000 on every save.
    # Rounded UP (ROUND_CEILING) so an exact price such as 5,000 BoloUp = 77 KES
    # never turns into 78 because of a tiny rounding difference.
    def save(self, *args, **kwargs):
        self.conversion_rate = (Decimal(1000) / self.price_per_1000).quantize(
            Decimal("0.0001"), rounding=ROUND_CEILING
        )
        super().save(*args, **kwargs)

        # ---- Whole-shilling packs (no rounding) --------------------------------
    @property
    def pack_coins(self) -> int:
        """
        Smallest number of coins whose price is a WHOLE number of shillings.
        Example: 15.4 per 1,000 = 77/5, so every 5 blocks (5,000 coins) costs 77 KES.
        """
        return Fraction(str(self.price_per_1000)).denominator * 1000

    @property
    def pack_price_kes(self) -> int:
        """Price (whole KES) of one pack."""
        return int(Fraction(str(self.price_per_1000)) * self.pack_coins / 1000)

    @property
    def min_coins(self) -> int:
        """Minimum purchase = one pack."""
        return self.pack_coins

    @property
    def step_coins(self) -> int:
        """Purchases grow in whole packs."""
        return self.pack_coins

    def clean(self):
        super().clean()
        if self.price_per_1000 and self.pack_coins > MAX_PACK_COINS:
            raise ValidationError({
                "price_per_1000": (
                    f"With this price the smallest whole-shilling pack would be {self.pack_coins:,} coins "
                    f"(limit {MAX_PACK_COINS:,}). Use a price with fewer decimals, e.g. 15.4 or 1.6."
                )
            })

    def calculate_kes(self, coins: int) -> int:
        """KES for the given coins. Exact for valid packs; rounds up only if given an odd amount."""
        amount = self.price_per_1000 * Decimal(coins) / Decimal(1000)
        return int(amount.to_integral_value(rounding=ROUND_CEILING))