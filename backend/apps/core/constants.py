"""
CoinHub shared constants.
"""

# Order statuses
ORDER_PENDING = "pending"
ORDER_PAID = "paid"
ORDER_LOADED = "loaded"
ORDER_FAILED = "failed"

ORDER_STATUS_CHOICES = [
    (ORDER_PENDING, "Pending"),
    (ORDER_PAID, "Paid"),
    (ORDER_LOADED, "Loaded"),
    (ORDER_FAILED, "Failed"),
]

# Payment statuses
PAYMENT_PENDING = "pending"
PAYMENT_SUCCESS = "success"
PAYMENT_FAILED = "failed"
PAYMENT_CANCELLED = "cancelled"

PAYMENT_STATUS_CHOICES = [
    (PAYMENT_PENDING, "Pending"),
    (PAYMENT_SUCCESS, "Success"),
    (PAYMENT_FAILED, "Failed"),
    (PAYMENT_CANCELLED, "Cancelled"),
]
