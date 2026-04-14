import stripe
from django.conf import settings
from .base import BasePaymentProvider


class StripePaymentProvider(BasePaymentProvider):
    def __init__(self):
        stripe_conf = settings.PAYMENT_GATEWAY_PROVIDERS.get("stripe", {})
        stripe.api_key = stripe_conf.get("secret_key")

    def create_payment(self, order_id: str, amount: float, currency: str, **kwargs) -> dict:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency=currency,
            metadata={"order_id": order_id},
        )
        return {
            "order_id": order_id,
            "transaction_id": payment_intent.id,
            "amount": amount,
            "currency": currency,
            "status": payment_intent.status,
            "metadata": payment_intent,
        }

    def verify_payment(self, order_id: str, transaction_id: str, **kwargs) -> dict:
        payment_intent = stripe.PaymentIntent.retrieve(transaction_id)
        status = "completed" if payment_intent.status == "succeeded" else payment_intent.status
        return {
            "order_id": order_id,
            "transaction_id": transaction_id,
            "status": status,
            "metadata": payment_intent,
        }

    def refund(self, order_id: str, transaction_id: str, amount: float, **kwargs) -> dict:
        refund = stripe.Refund.create(payment_intent=transaction_id, amount=int(amount * 100))
        return {
            "order_id": order_id,
            "transaction_id": transaction_id,
            "status": "refunded",
            "amount": amount,
            "metadata": refund,
        }
