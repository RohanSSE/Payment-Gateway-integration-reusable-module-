import razorpay
from django.conf import settings
from .base import BasePaymentProvider
from ..exceptions import PaymentProviderError


class RazorpayPaymentProvider(BasePaymentProvider):
    def __init__(self):
        providers = getattr(settings, "PAYMENT_GATEWAY_PROVIDERS", {})
        razorpay_conf = providers.get("razorpay", {})
        key_id = razorpay_conf.get("key_id") or razorpay_conf.get("KEY_ID")
        key_secret = razorpay_conf.get("key_secret") or razorpay_conf.get("KEY_SECRET")
        if not key_id or not key_secret:
            raise PaymentProviderError("Razorpay credentials are missing in PAYMENT_GATEWAY_PROVIDERS.")
        self.client = razorpay.Client(auth=(key_id, key_secret))

    def create_payment(self, order_id: str, amount: float, currency: str, **kwargs) -> dict:
        value = int(amount * 100)
        try:
            order = self.client.order.create({
                "amount": value,
                "currency": currency,
                "receipt": order_id,
                "payment_capture": 1,
            })
        except Exception as exc:
            raise PaymentProviderError(str(exc)) from exc
        return {
            "order_id": order_id,
            "transaction_id": order.get("id"),
            "amount": amount,
            "currency": currency,
            "status": "created",
            "metadata": order,
        }

    def verify_payment(self, order_id: str, transaction_id: str, **kwargs) -> dict:
        try:
            payment = self.client.payment.fetch(transaction_id)
        except Exception as exc:
            raise PaymentProviderError(str(exc)) from exc
        status = "completed" if payment.get("status") == "captured" else "pending"
        return {
            "order_id": order_id,
            "transaction_id": transaction_id,
            "status": status,
            "metadata": payment,
        }

    def refund(self, order_id: str, transaction_id: str, amount: float, **kwargs) -> dict:
        value = int(amount * 100)
        try:
            refund = self.client.payment.refund(transaction_id, {"amount": value})
        except Exception as exc:
            raise PaymentProviderError(str(exc)) from exc
        return {
            "order_id": order_id,
            "transaction_id": transaction_id,
            "status": "refunded",
            "amount": amount,
            "metadata": refund,
        }
