import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.core.utils import generate_reference
from apps.payments.models import Payment
from apps.payments.daraja import initiate_stk_push
from .models import Order
from .serializers import RechargeRequestSerializer, OrderStatusSerializer

logger = logging.getLogger(__name__)


class RechargeCreateView(APIView):
    """
    POST /api/recharges/

    Validates request, calculates KES amount server-side,
    creates Order + Payment records, and initiates Daraja STK push.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RechargeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        coin_type = data["coin_type_slug"]  # already resolved to CoinType object
        app_user_id = data["app_user_id"]
        phone_number = data["phone_number"]
        coins_requested = data["coins_requested"]

        # ── Server-side amount calculation (never trust the client) ──
        amount_kes = coin_type.calculate_kes(coins_requested)

        # ── Create Order ──────────────────────────────────────────────
        reference = generate_reference()
        order = Order.objects.create(
            reference=reference,
            coin_type=coin_type,
            app_user_id=app_user_id,
            phone_number=phone_number,
            coins_requested=coins_requested,
            amount_paid=amount_kes,
        )

        # ── Create Payment record ────────────────────────────────────
        payment = Payment.objects.create(
            order=order,
            phone_number=phone_number,
            amount=amount_kes,
        )

        # ── Initiate Daraja STK Push ──────────────────────────────────
        try:
            stk_result = initiate_stk_push(
                phone=phone_number,
                amount=int(amount_kes),
                reference=reference,
                description=f"CoinHub {coin_type.name} recharge",
            )
            payment.checkout_request_id = stk_result.get("CheckoutRequestID", "")
            payment.merchant_request_id = stk_result.get("MerchantRequestID", "")
            payment.save(update_fields=["checkout_request_id", "merchant_request_id"])
        except Exception as exc:
            logger.exception("Daraja STK push failed for order %s: %s", reference, exc)
            # Don't fail the request — let the user see the pending state
            # and admin can investigate via the callback or manually.

        return Response(
            {
                "reference": reference,
                "amount_kes": amount_kes,
                "message": "Payment initiated. Check your phone for the M-Pesa prompt.",
            },
            status=status.HTTP_201_CREATED,
        )


class PaymentStatusView(APIView):
    """
    GET /api/payment-status/<reference>/

    Allows the frontend to poll for payment confirmation.
    """
    permission_classes = [AllowAny]

    def get(self, request, reference):
        try:
            order = Order.objects.select_related("coin_type", "payment").get(
                reference=reference
            )
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderStatusSerializer(order)
        return Response(serializer.data)
