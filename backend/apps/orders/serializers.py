import re
from rest_framework import serializers
from apps.catalog.models import CoinType
from .models import Order


class RechargeRequestSerializer(serializers.Serializer):
    """Input serializer for POST /api/recharges/"""

    coin_type_slug = serializers.SlugField()
    app_user_id = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=20)
    coins_requested = serializers.IntegerField(min_value=1)

    def validate_coin_type_slug(self, value):
        try:
            coin_type = CoinType.objects.get(slug=value, active=True)
        except CoinType.DoesNotExist:
            raise serializers.ValidationError("Coin type not found or inactive.")
        return coin_type

    def validate_app_user_id(self, value):
        """Validates that the App User ID is between 1 and 10 digits, numbers only."""
        clean_value = str(value).strip()

        if not re.match(r'^\d{1,10}$', clean_value):
            raise serializers.ValidationError(
                "App User ID must be between 1 and 10 digits long and contain only numbers."
            )
        return clean_value

    def validate_phone_number(self, value):
        from apps.core.utils import normalize_phone
        phone = normalize_phone(value)
        if not phone.startswith("2547") and not phone.startswith("2541"):
            raise serializers.ValidationError("Enter a valid Kenyan M-Pesa number.")
        if len(phone) != 12:
            raise serializers.ValidationError("Phone number must be 12 digits including country code.")
        return phone


class OrderStatusSerializer(serializers.ModelSerializer):
    """Output serializer for GET /api/payment-status/<ref>/"""

    coin_type_name = serializers.CharField(source="coin_type.name")
    payment_status = serializers.SerializerMethodField()
    mpesa_receipt = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "reference",
            "coin_type_name",
            "app_user_id",
            "coins_requested",
            "amount_paid",
            "status",
            "payment_status",
            "mpesa_receipt",
            "created_at",
        ]

    def get_payment_status(self, obj):
        payment = getattr(obj, "payment", None)
        if payment:
            return payment.status
        return "pending"

    def get_mpesa_receipt(self, obj):
        payment = getattr(obj, "payment", None)
        if payment:
            return payment.mpesa_receipt
        return None
