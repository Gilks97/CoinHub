"""
CoinHub payments views — Daraja callback handler.
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from apps.core.constants import PAYMENT_SUCCESS, PAYMENT_FAILED, ORDER_PAID, ORDER_FAILED
from .models import Payment

logger = logging.getLogger(__name__)


class DarajaCallbackView(APIView):
    """
    POST /api/payments/callback/

    Receives STK Push result from Safaricom Daraja.
    Marks the Payment and Order as paid or failed accordingly.

    Safaricom expects a 200 OK with {"ResultCode": 0, "ResultDesc": "Success"}
    """
    permission_classes = [AllowAny]
    # Disable CSRF for this endpoint — it's called by Safaricom servers
    authentication_classes = []

    def post(self, request):
        data = request.data
        logger.info("Daraja callback received: %s", data)

        try:
            stk_callback = data["Body"]["stkCallback"]
            result_code = stk_callback.get("ResultCode")
            checkout_request_id = stk_callback.get("CheckoutRequestID")

            try:
                payment = Payment.objects.select_related("order").get(
                    checkout_request_id=checkout_request_id
                )
            except Payment.DoesNotExist:
                logger.warning("Callback for unknown CheckoutRequestID: %s", checkout_request_id)
                return Response({"ResultCode": 0, "ResultDesc": "Accepted"})

            # Always store the raw callback for audit
            payment.raw_callback_json = data

            if result_code == 0:
                # Successful payment
                callback_metadata = stk_callback.get("CallbackMetadata", {})
                items = {
                    item["Name"]: item.get("Value")
                    for item in callback_metadata.get("Item", [])
                }
                payment.mpesa_receipt = items.get("MpesaReceiptNumber", "")
                payment.status = PAYMENT_SUCCESS
                payment.save(update_fields=["mpesa_receipt", "status", "raw_callback_json"])

                # Update order status
                payment.order.status = ORDER_PAID
                payment.order.save(update_fields=["status"])
                logger.info(
                    "Payment SUCCESS for order %s | receipt=%s",
                    payment.order.reference,
                    payment.mpesa_receipt,
                )
            else:
                # Failed / cancelled
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
            logger.exception("Malformed Daraja callback: %s", exc)

        # Always acknowledge Safaricom
        return Response({"ResultCode": 0, "ResultDesc": "Accepted"})


class PaymentStatusView(APIView):
    """
    GET /api/payment-status/<reference>/

    Thin status check — used by frontend polling.
    Kept here for import compatibility; actual view logic is in orders/views.py.
    """
    pass
