# Payment Gateway Integration Reusable Module

Reusable Django app for multi-provider payment integration (Stripe + Razorpay) with DRF APIs.

## Installation

- Add app to your project INSTALLED_APPS:

`python
INSTALLED_APPS = [
    # ...
    " payment_gateway\,
]
`

- Set up provider configuration in settings.py:

`python
PAYMENT_GATEWAY_DEFAULT_PROVIDER = \razorpay\
PAYMENT_GATEWAY_PROVIDERS = {
 \razorpay\: {
 \key_id\: \rzp_test_xxx\,
 \key_secret\: \yyy\,
 \webhook_secret\: \zzz\,
 },
 \stripe\: {
 \secret_key\: \sk_test_xxx\,
 \webhook_secret\: \whsec_yyy\,
 },
}
`

- Include URLs:

`python
from django.urls import path, include

urlpatterns = [
 # ...
 path(\api/payments/\, include(\payment_gateway.urls\)),
]
`

## Endpoints

- POST /api/payments/create/ -> create payment
- POST /api/payments/verify/ -> verify payment
- POST /api/payments/refund/ -> refund payment
- POST /api/payments/webhook/razorpay/
- POST /api/payments/webhook/stripe/

## App structure

- payment_gateway/models.py: PaymentRecord
- payment_gateway/services: provider base, razorpay, stripe, factory
- payment_gateway/webhooks: webhook views + signals
- payment_gateway/views.py: DRF endpoints
- payment_gateway/serializers.py: request and response serializers
- payment_gateway/exceptions: custom errors
- payment_gateway/utils: settings utilities

## License

MIT
