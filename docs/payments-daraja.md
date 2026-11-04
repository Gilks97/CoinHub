# Payments and Daraja

CoinHub collects payments with **M-Pesa Express (STK Push)** from Safaricom's Daraja API, using the **Buy Goods (till)** transaction type.

## Money flow

```
Customer's phone ──(PIN)──► Safaricom ──► your till
                                │
                    callback ───┘──► POST /api/payments/daraja/callback/
```

CoinHub never sees the customer's PIN or any card data.

## What is sent to Daraja

`backend/apps/payments/daraja.py` builds the request:

| Field | Value |
|---|---|
| `BusinessShortCode` | `DARAJA_SHORTCODE` (the Store / Head Office number for a till) |
| `Password` | `base64(BusinessShortCode + Passkey + Timestamp)` |
| `Timestamp` | Current time as `YYYYMMDDHHMMSS` |
| `TransactionType` | `CustomerBuyGoodsOnline` (required for tills) |
| `Amount` | Whole shillings (integer) |
| `PartyA` / `PhoneNumber` | Customer number, `254XXXXXXXXX` |
| `PartyB` | `DARAJA_TILL_NUMBER` |
| `CallBackURL` | `DARAJA_CALLBACK_URL` |
| `AccountReference` | The order reference (for example `CH2410260001`) |
| `TransactionDesc` | Short text with the coin name |

First CoinHub requests an OAuth access token using the consumer key and secret, then posts the STK request. Both calls have timeouts.

## Two responses, two places to look

1. **Immediate response** (synchronous): `ResponseCode "0"` means Safaricom *accepted the request*, not that the customer paid. Errors such as a wrong password or credentials appear here.
2. **Callback** (asynchronous, usually within seconds): the real result. `ResultCode 0` means paid.

Both are stored on the payment (`response_payload` and `callback_payload`) and are visible, formatted, in the admin under **Payments**. This is the first place to look when a payment misbehaves.

## Callback handling

`DarajaCallbackView` (`backend/apps/payments/views.py`):

- runs in `transaction.atomic()` and locks the payment row (`select_for_update`),
- skips payments that are already final (so retries are harmless),
- records result code, description, receipt and the raw payload,
- moves Payment and Order to their next states,
- always replies with an "Accepted" body.

## Result codes you will see

| Code | Typical meaning |
|---|---|
| `0` | Success |
| `1032` | Customer cancelled the prompt |
| `1037` | Prompt timed out (customer did not respond) |
| `1` | Insufficient balance |
| `2001` | Wrong PIN |
| `4999` | Seen in CoinHub logs together with the description "Merchant does not exist" |

Always read `result_description` on the payment. It is more reliable than the number. Safaricom may add codes over time.

## Setting up Daraja

1. Create an app on the Safaricom Developer Portal and enable **Lipa Na M-Pesa Online**.
2. For testing, use `DARAJA_ENV=sandbox` with the sandbox shortcode `174379` and the sandbox passkey.
3. To go live, complete Safaricom's Go Live process for your till so you receive the production consumer key, secret, shortcode and passkey.
4. Set `DARAJA_ENV=production` and all values in the environment (see [Configuration](configuration.md)).
5. Make sure `DARAJA_CALLBACK_URL` is publicly reachable over HTTPS.

## Till numbers: the number mix-up

For a till, two different numbers are involved:

| Setting | Number |
|---|---|
| `DARAJA_SHORTCODE` (`BusinessShortCode`) | Store / Head Office number. It must belong to the passkey |
| `DARAJA_TILL_NUMBER` (`PartyB`) | The till number that receives the money |

If the till is not registered under that Head Office, or is not enabled for M-Pesa Express, Safaricom accepts the request and then reports "Merchant does not exist" in the callback. See the troubleshooting steps below.

## Troubleshooting payments

| Symptom | Likely cause and action |
|---|---|
| Callback says "Merchant does not exist" | `PartyB` (till) is not linked to `BusinessShortCode`, the till is not enabled for STK, or sandbox and production values are mixed. Check the Head Office/till relationship with Safaricom; contact Daraja support with the `CheckoutRequestID` |
| Immediate response is an error (token or credentials) | Consumer key/secret do not match `DARAJA_ENV`, or the passkey does not belong to the shortcode |
| Customer gets no prompt | Wrong phone number, phone off or out of coverage, or the request was rejected (see `response_payload`) |
| Order stays `pending` | Callback never arrived: check `DARAJA_CALLBACK_URL`, that the backend is awake and public, and the Render logs |
| Customer paid but order is `failed` | Rare. Compare the M-Pesa receipt with the payment record, then escalate to the technician (see below) |
| Order `paid` but customer says no coins | Normal until staff press Ship Coins; coins are loaded manually |

## Reconciliation and known limitations

- There is currently **no automatic re-check** (STK Query) of payments that stay `pending`. If a callback is lost, the order must be checked manually against the till statement.
- The callback is accepted without verifying the amount or phone against the order. See the roadmap in [Security](security.md).
- Amounts are whole shillings, rounded up from the exact price, because STK Push cannot charge fractions.

## Money-handling rules for operators

- Match each `paid` order to the M-Pesa receipt shown in the admin before loading coins when in doubt.
- Never edit payment or order amounts by hand. The Payment admin is read-only on purpose.
- Keep the Daraja credentials only in the hosting environment variables.
