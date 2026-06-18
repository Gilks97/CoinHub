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
from django.utils import timezone

from apps.core.constants import PAYMENT_SUCCESS, PAYMENT_FAILED, ORDER_PAID, ORDER_FAILED
from .models import Payment

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class DarajaCallbackView(APIView):
    """
    POST /api/payments/daraja/callback/
    Receives STK Push result from Safaricom Daraja securely inside an atomic block.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        data = request.data

        try:
            stk_callback = data["Body"]["stkCallback"]
            result_code = stk_callback.get("ResultCode")
            checkout_request_id = stk_callback.get("CheckoutRequestID")

            with transaction.atomic():
                try:
                    payment = Payment.objects.select_related("order").select_for_update().get(
                        checkout_request_id=checkout_request_id
                    )
                except Payment.DoesNotExist:
                    logger.warning("Callback ignored | Unknown CheckoutRequestID: %s", checkout_request_id)
                    return Response({"ResultCode": 0, "ResultDesc": "Accepted"})

                if payment.status in [PAYMENT_SUCCESS, PAYMENT_FAILED]:
                    return Response({"ResultCode": 0, "ResultDesc": "Accepted"})

                # Populate reconciliation and historical audit metrics
                payment.callback_payload = data
                payment.raw_callback_json = data 
                payment.callback_received_at = timezone.now()
                payment.result_code = result_code
                payment.result_description = stk_callback.get("ResultDesc")

                if result_code == 0:
                    callback_metadata = stk_callback.get("CallbackMetadata", {})
                    items = {
                        item["Name"]: item.get("Value")
                        for item in callback_metadata.get("Item", [])
                    }
                    payment.mpesa_receipt = items.get("MpesaReceiptNumber", "")
                    payment.status = PAYMENT_SUCCESS
                    payment.save(update_fields=[
                        "mpesa_receipt", "status", "callback_payload", 
                        "callback_received_at", "result_code", "result_description", "raw_callback_json"
                    ])

                    payment.order.status = ORDER_PAID
                    payment.order.save(update_fields=["status"])
                    
                    logger.info("Payment SUCCESS | Order %s | Receipt %s", payment.order.reference, payment.mpesa_receipt)
                else:
                    payment.status = PAYMENT_FAILED
                    payment.save(update_fields=[
                        "status", "callback_payload", "callback_received_at", 
                        "result_code", "result_description", "raw_callback_json"
                    ])
                    
                    payment.order.status = ORDER_FAILED
                    payment.order.save(update_fields=["status"])
                    
                    logger.warning("Payment FAILED | Order %s | ResultCode %s", payment.order.reference, result_code)

        except (KeyError, TypeError) as exc:
            logger.exception("Malformed Daraja callback payload structure dropped.")

        return Response({"ResultCode": 0, "ResultDesc": "Accepted"})


class PaymentStatusView(APIView):
    """
    GET /api/payment-status/<reference>/

    Thin status check — used by frontend polling.
    Kept here for import compatibility; actual view logic is in orders/views.py.
    """
    pass
