"""
CoinHub REST API URL Routes
"""
from django.urls import path
from apps.catalog.views import CoinTypeListView
from apps.orders.views import RechargeCreateView, PaymentStatusView
from apps.payments.views import DarajaCallbackView

urlpatterns = [
    # GET  /api/coins/               — list active coin types and rates
    path("coins/", CoinTypeListView.as_view(), name="api-coins"),
    # POST /api/recharges/           — create order + initiate STK push
    path("recharges/", RechargeCreateView.as_view(), name="api-recharges"),
    # GET  /api/payment-status/<ref>/— poll payment status by order reference
    path("payment-status/<str:reference>/", PaymentStatusView.as_view(), name="api-payment-status"),
    # POST /api/payments/callback/   — Daraja STK callback (Safaricom → CoinHub)
    path("payments/daraja/callback/", DarajaCallbackView.as_view(), name="api-payments-callback"),
]
