"""
Safaricom Daraja STK Push integration.

Docs:
https://developer.safaricom.co.ke/APIs/MpesaExpressSimulate
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
    url = SANDBOX_BASE if env == "sandbox" else PRODUCTION_BASE

    logger.info(
        "Daraja environment selected | ENV=%s | BASE_URL=%s",
        env,
        url,
    )
    return url


def _get_access_token() -> str:
    """
    Obtain a Daraja OAuth access token.
    """
    consumer_key = settings.DARAJA["CONSUMER_KEY"]
    consumer_secret = settings.DARAJA["CONSUMER_SECRET"]

    url = f"{_base_url()}/oauth/v1/generate?grant_type=client_credentials"

    logger.info("STEP 1/4 - Requesting OAuth token")
    logger.info("OAuth URL: %s", url)

    try:
        response = requests.get(
            url,
            auth=(consumer_key, consumer_secret),
            timeout=15,
        )

        logger.info(
            "OAuth response received | HTTP %s",
            response.status_code,
        )

        response.raise_for_status()
        token_data = response.json()

        logger.info(
            "STEP 1/4 COMPLETE - OAuth token acquired | expires_in=%s",
            token_data.get("expires_in"),
        )

        return token_data["access_token"]

    except requests.HTTPError as exc:
        logger.error(
            "OAuth request failed | HTTP=%s | BODY=%s",
            exc.response.status_code if exc.response else "N/A",
            exc.response.text if exc.response else "NO RESPONSE",
            exc_info=True,
        )
        raise
    except Exception:
        logger.exception("Unexpected error while obtaining OAuth token")
        raise


def _generate_password(timestamp: str) -> str:
    """
    Generate Daraja password.
    Base64(Shortcode + Passkey + Timestamp)
    """
    shortcode = settings.DARAJA["SHORTCODE"]
    passkey = settings.DARAJA["PASSKEY"]

    raw = f"{shortcode}{passkey}{timestamp}"
    password = base64.b64encode(raw.encode()).decode()

    logger.info(
        "STEP 2/4 - Password generated | shortcode=%s | timestamp=%s",
        shortcode,
        timestamp,
    )

    return password


def initiate_stk_push(
    phone: str,
    amount: int,
    reference: str,
    description: str,
) -> dict:
    """
    Initiate STK Push.
    """
    logger.info("=" * 80)
    logger.info("STK PUSH INITIALIZATION STARTED")
    logger.info("Reference      : %s", reference)
    logger.info("Phone          : %s", phone)
    logger.info("Amount         : %s", amount)
    logger.info("Description    : %s", description)
    logger.info("=" * 80)

    try:
        token = _get_access_token()
    except Exception:
        logger.exception(
            "STK initialization aborted. OAuth token acquisition failed."
        )
        raise

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = _generate_password(timestamp)

    shortcode = settings.DARAJA["SHORTCODE"]
    callback_url = settings.DARAJA["CALLBACK_URL"]

    logger.info(
        "STEP 3/4 - Building STK payload | shortcode=%s (Paybill Mode)",
        shortcode,
    )
    logger.info(
        "Configured callback URL: %s",
        callback_url,
    )

    # ─────────────────────────────────────────────────────────────────────────
    # 🛠️ PAYBILL REFRACTOR COMPLETED HERE
    # ─────────────────────────────────────────────────────────────────────────
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",  # Switched to Paybill
        "Amount": amount,
        "PartyA": phone,
        "PartyB": shortcode,                         # For Paybill, PartyB matches the shortcode
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": reference,
        "TransactionDesc": description[:13],
    }

    log_payload = payload.copy()
    log_payload["Password"] = "[REDACTED]"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    url = f"{_base_url()}/mpesa/stkpush/v1/processrequest"

    logger.info("STEP 4/4 - Sending STK request")
    logger.info("Daraja URL: %s", url)
    logger.info("Payload: %s", log_payload)

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30,
        )

        logger.info(
            "Daraja responded | HTTP=%s",
            response.status_code,
        )

        logger.info(
            "Daraja raw response body: %s",
            response.text,
        )

        if not response.ok:
            logger.error(
                "Daraja returned error response | HTTP=%s | BODY=%s",
                response.status_code,
                response.text,
            )

        response.raise_for_status()
        data = response.json()

        logger.info(
            "Raw Daraja Response: %s",
            data,
        )

        response_code = data.get("ResponseCode")

        if response_code == "0":
            logger.info("STK PUSH ACCEPTED")
            logger.info("MerchantRequestID=%s", data.get("MerchantRequestID"))
            logger.info("CheckoutRequestID=%s", data.get("CheckoutRequestID"))
            logger.info("Customer should receive M-Pesa prompt shortly.")
        else:
            logger.warning("Daraja returned non-success response.")
            logger.warning("ResponseCode=%s", response_code)
            logger.warning("ResponseDescription=%s", data.get("ResponseDescription"))

        return data

    except requests.HTTPError as exc:
        logger.error(
            "STK request failed | HTTP=%s | BODY=%s",
            exc.response.status_code if exc.response else "N/A",
            exc.response.text if exc.response else "NO RESPONSE",
            exc_info=True,
        )
        raise
    except Exception:
        logger.exception("Unexpected exception while sending STK request")
        raise
    finally:
        logger.info(
            "STK PUSH PROCESS COMPLETED FOR REFERENCE=%s",
            reference,
        )
        logger.info("=" * 80)