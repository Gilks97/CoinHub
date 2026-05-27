"""
Safaricom Daraja STK Push integration.

Docs: https://developer.safaricom.co.ke/APIs/MpesaExpressSimulate
"""
import base64
import logging
from datetime import datetime

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

SANDBOX_BASE = "https://sandbox.safaricom.co.ke"
PRODUCTION_BASE = "https://api.safaricom.co.ke"


def _base_url() -> str:
    env = settings.DARAJA.get("ENV", "sandbox")
    return SANDBOX_BASE if env == "sandbox" else PRODUCTION_BASE


def _get_access_token() -> str:
    """Obtain a Daraja OAuth access token."""
    consumer_key = settings.DARAJA["CONSUMER_KEY"]
    consumer_secret = settings.DARAJA["CONSUMER_SECRET"]
    url = f"{_base_url()}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(consumer_key, consumer_secret), timeout=15)
    response.raise_for_status()
    return response.json()["access_token"]


def _generate_password(timestamp: str) -> str:
    """
    Generate the Base64-encoded Daraja password.
    Formula: Base64(Shortcode + Passkey + Timestamp)
    """
    shortcode = settings.DARAJA["SHORTCODE"]
    passkey = settings.DARAJA["PASSKEY"]
    raw = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(raw.encode()).decode()


def initiate_stk_push(phone: str, amount: int, reference: str, description: str) -> dict:
    """
    Initiate a Lipa Na M-Pesa Online (STK Push) to a Till Number.

    :param phone:       Phone number in 2547XXXXXXXX format.
    :param amount:      Amount in KES (integer).
    :param reference:   CoinHub order reference e.g. CH2605250001.
    :param description: Human-readable payment description.
    :returns:           Daraja API response dict.
    :raises:            requests.HTTPError on non-2xx response.
    """
    token = _get_access_token()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = _generate_password(timestamp)

    shortcode = settings.DARAJA["SHORTCODE"]
    till = settings.DARAJA["TILL_NUMBER"]
    callback_url = settings.DARAJA["CALLBACK_URL"]

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerBuyGoodsOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": till,
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": reference,
        "TransactionDesc": description[:13],  # Daraja max 13 chars
    }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"{_base_url()}/mpesa/stkpush/v1/processrequest"

    logger.info("Initiating STK push for %s | amount=KES %s | phone=%s", reference, amount, phone)
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    logger.info("STK push response for %s: %s", reference, data)
    return data
