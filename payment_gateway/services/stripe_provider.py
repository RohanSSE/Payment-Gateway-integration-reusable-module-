import stripe
from django.conf import settings
from .base import BasePaymentProvider
from ..exceptions import PaymentProviderError


class StripePaymentProvider(BasePaymentProvider):
    def __init__(self):
        providers = getattr(settings, "PAYMENT_GATEWAY_PROVIDERS", {})
        stripe_conf = providers.get("stripe", {})
        api_key = stripe_conf.get("secret_key") or stripe_conf.get("SECRET_KEY")
        if not api_key:
            raise PaymentProviderError("Stripe secret key is missing in PAYMENT_GATEWAY_PROVIDERS.")
        stripe.api_key = api_key

    def create_payment(self, order_id: str, amount: float, currency: str, **kwargs) -> dict:
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency=currency,
                metadata={"order_id": order_id},
            )
        except Exception as exc:
            raise PaymentProviderError(str(exc)) from exc

        status = "success" if payment_intent.status == "succeeded" else "created"
        return {
            "order_id": order_id,
            "transaction_id": payment_intent.id,
            "payment_id": payment_intent.id,
            "amount": amount,
            "currency": currency,
            "status": status,
            "metadata": payment_intent.to_dict_recursive(),
        }

    def verify_payment(self, order_id: str, transaction_id: str, **kwargs) -> dict:
        try:
            payment_intent = stripe.PaymentIntent.retrieve(transaction_id)
        except Exception as exc:
            raise PaymentProviderError(str(exc)) from exc
        status = "success" if payment_intent.status == "succeeded" else "failed"
        return {
            "order_id": order_id,
            "transaction_id": transaction_id,
            "payment_id": transaction_id,
            "status": status,
            "metadata": payment_intent.to_dict_recursive(),
        }

    def refund(self, order_id: str, transaction_id: str, amount: float, **kwargs) -> dict:
        try:
            refund = stripe.Refund.create(payment_intent=transaction_id, amount=int(amount * 100))
        except Exception as exc:
            raise PaymentProviderError(str(exc)) from exc
        return {
            "order_id": order_id,
            "transaction_id": transaction_id,
            "payment_id": transaction_id,
            "status": "refunded",
            "amount": amount,
            "metadata": refund.to_dict_recursive(),
        }
