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
    Creates Order + Payment + triggers STK Push
    """
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("=" * 80)
        logger.info("RECHARGE FLOW STARTED")
        logger.info("Incoming request data: %s", request.data)
        logger.info("=" * 80)

        serializer = RechargeRequestSerializer(data=request.data)

        # ─────────────────────────────────────────────
        # 1. Validation
        # ─────────────────────────────────────────────
        if not serializer.is_valid():
            logger.warning(
                "RECHARGE VALIDATION FAILED | errors=%s | input=%s",
                serializer.errors,
                request.data,
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        logger.info("Validation successful")

        data = serializer.validated_data

        coin_type = data["coin_type_slug"]
        app_user_id = data["app_user_id"]
        phone_number = data["phone_number"]
        coins_requested = data["coins_requested"]

        logger.info(
            "Parsed data | user_id=%s | phone=%s | coins=%s | coin_type=%s",
            app_user_id,
            phone_number,
            coins_requested,
            getattr(coin_type, "slug", str(coin_type)),
        )

        # ─────────────────────────────────────────────
        # 2. Amount calculation
        # ─────────────────────────────────────────────
        try:
            amount_kes = coin_type.calculate_kes(coins_requested)
            logger.info(
                "Amount calculated successfully | coins=%s | amount_kes=%s",
                coins_requested,
                amount_kes,
            )
        except Exception:
            logger.exception(
                "FAILED during KES calculation | coin_type=%s | coins=%s",
                coin_type,
                coins_requested,
            )
            return Response(
                {"error": "Failed to calculate amount"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ─────────────────────────────────────────────
        # 3. Order creation
        # ─────────────────────────────────────────────
        reference = generate_reference()

        logger.info("Generating order | reference=%s", reference)

        try:
            order = Order.objects.create(
                reference=reference,
                coin_type=coin_type,
                app_user_id=app_user_id,
                phone_number=phone_number,
                coins_requested=coins_requested,
                amount_paid=amount_kes,
            )

            logger.info(
                "Order created successfully | order_id=%s | reference=%s",
                order.id,
                reference,
            )
        except Exception:
            logger.exception("ORDER CREATION FAILED | reference=%s", reference)
            return Response(
                {"error": "Order creation failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ─────────────────────────────────────────────
        # 4. Payment creation
        # ─────────────────────────────────────────────
        try:
            payment = Payment.objects.create(
                order=order,
                phone_number=phone_number,
                amount=amount_kes,
            )

            logger.info(
                "Payment record created | payment_id=%s | order=%s",
                payment.id,
                reference,
            )
        except Exception:
            logger.exception(
                "PAYMENT CREATION FAILED | reference=%s",
                reference,
            )
            return Response(
                {"error": "Payment creation failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ─────────────────────────────────────────────
        # 5. STK Push
        # ─────────────────────────────────────────────
        logger.info("Initiating STK Push | reference=%s", reference)

        try:
            stk_result = initiate_stk_push(
                phone=phone_number,
                amount=int(amount_kes),
                reference=reference,
                description=f"CoinHub {coin_type.name} recharge",
            )

            logger.info(
                "STK push completed | reference=%s | response=%s",
                reference,
                stk_result,
            )

            payment.checkout_request_id = stk_result.get("CheckoutRequestID", "")
            payment.merchant_request_id = stk_result.get("MerchantRequestID", "")
            payment.save(update_fields=["checkout_request_id", "merchant_request_id"])

            logger.info(
                "Payment updated with STK IDs | checkout_request_id=%s | merchant_request_id=%s",
                payment.checkout_request_id,
                payment.merchant_request_id,
            )

        except Exception:
            logger.exception(
                "STK PUSH FAILED | reference=%s | order_id=%s | payment_id=%s",
                reference,
                getattr(order, "id", None),
                getattr(payment, "id", None),
            )

        # ─────────────────────────────────────────────
        # 6. Final response
        # ─────────────────────────────────────────────
        logger.info("RECHARGE FLOW COMPLETED | reference=%s", reference)
        logger.info("=" * 80)

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
