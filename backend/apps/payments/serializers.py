from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    order_reference = serializers.CharField(source="order.reference", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order_reference",
            "checkout_request_id",
            "merchant_request_id",
            "mpesa_receipt",
            "phone_number",
            "amount",
            "status",
            "created_at",
        ]
