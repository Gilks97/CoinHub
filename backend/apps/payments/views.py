"""
CoinHub payments views — Daraja callback handler.
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from apps.core.constants import PAYMENT_SUCCESS, PAYMENT_FAILED, ORDER_PAID, ORDER_FAILED
from .models import Payment

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class DarajaCallbackView(APIView):
    """
    POST /api/payments/daraja/callback/
    Receives STK Push result from Safaricom Daraja safely inside a transaction database block.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        data = request.data
        logger.info("Daraja callback received: %s", data)

        try:
            stk_callback = data["Body"]["stkCallback"]
            result_code = stk_callback.get("ResultCode")
            checkout_request_id = stk_callback.get("CheckoutRequestID")

            # ─────────────────────────────────────────────────────────────────
            # 🔒 ATOMIC TRANSACTION WITH FOR-UPDATE LOCKING
            # ─────────────────────────────────────────────────────────────────
            with transaction.atomic():
                try:
                    # Lock the specific payment row during processing to block race-conditions
                    payment = Payment.objects.select_related("order").select_for_update().get(
                        checkout_request_id=checkout_request_id
                    )
                except Payment.DoesNotExist:
                    logger.warning("Callback for unknown CheckoutRequestID: %s", checkout_request_id)
                    return Response({"ResultCode": 0, "ResultDesc": "Accepted"})

                # Idempotency Check: Drop execution cleanly if this state was already mutation-processed
                if payment.status in [PAYMENT_SUCCESS, PAYMENT_FAILED]:
                    logger.info("Callback for transaction %s already finalized. Skipping state update.", checkout_request_id)
                    return Response({"ResultCode": 0, "ResultDesc": "Accepted"})

                # Always store the raw callback for audit compliance
                payment.raw_callback_json = data

                if result_code == 0:
                    # Successful payment parsing
                    callback_metadata = stk_callback.get("CallbackMetadata", {})
                    items = {
                        item["Name"]: item.get("Value")
                        for item in callback_metadata.get("Item", [])
                    }
                    payment.mpesa_receipt = items.get("MpesaReceiptNumber", "")
                    payment.status = PAYMENT_SUCCESS
                    payment.save(update_fields=["mpesa_receipt", "status", "raw_callback_json"])

                    # Synchronously advance the parent Order status
                    payment.order.status = ORDER_PAID
                    payment.order.save(update_fields=["status"])
                    
                    logger.info(
                        "Payment SUCCESS for order %s | receipt=%s. Coins unlocked.",
                        payment.order.reference,
                        payment.mpesa_receipt,
                    )
                else:
                    # Failed, cancelled, or timed out at user handset layer
                    payment.status = PAYMENT_FAILED
                    payment.save(update_fields=["status", "raw_callback_json"])
                    
                    payment.order.status = ORDER_FAILED
                    payment.order.save(update_fields=["status"])
                    
                    logger.warning(
                        "Payment FAILED for order %s | ResultCode=%s",
                        payment.order.reference,
                        result_code,
                    )

        except (KeyError, TypeError) as exc:
            logger.exception("Malformed Daraja callback structure: %s", exc)

        # Always acknowledge Safaricom to prevent payload retries
        return Response({"ResultCode": 0, "ResultDesc": "Accepted"})


class PaymentStatusView(APIView):
    """
    GET /api/payment-status/<reference>/

    Thin status check — used by frontend polling.
    Kept here for import compatibility; actual view logic is in orders/views.py.
    """
    pass
