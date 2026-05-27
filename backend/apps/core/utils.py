"""
CoinHub core utilities.

Reference format: CH<DDMMYY><SEQUENCE>
Example: CH2605250001, CH2605250002
"""
from datetime import date


def generate_reference() -> str:
    """
    Generate a unique CoinHub transaction reference.
    Format: CH + DDMMYY + 4-digit zero-padded daily sequence.
    e.g. CH2605250001
    """
    from apps.orders.models import Order  # lazy import to avoid circular deps

    today = date.today()
    date_str = today.strftime("%d%m%y")
    prefix = f"CH{date_str}"

    # Count orders created today to determine next sequence number
    count = Order.objects.filter(reference__startswith=prefix).count()
    sequence = str(count + 1).zfill(4)
    return f"{prefix}{sequence}"


def normalize_phone(phone: str) -> str:
    """
    Normalise a phone number to the 2547XXXXXXXX format required by Daraja.
    Accepts: 07XXXXXXXX, 7XXXXXXXX, 2547XXXXXXXX, +2547XXXXXXXX
    """
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("+"):
        phone = phone[1:]
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    if phone.startswith("7") or phone.startswith("1"):
        phone = "254" + phone
    return phone
