import razorpay
from django.conf import settings
from .base import BasePaymentProvider


class RazorpayPaymentProvider(BasePaymentProvider):
    def __init__(self):
        razorpay_conf = settings.PAYMENT_GATEWAY_PROVIDERS.get("razorpay", {})
        self.client = razorpay.Client(auth=(razorpay_conf.get("key_id"), razorpay_conf.get("key_secret")))

    def create_payment(self, order_id: str, amount: float, currency: str, **kwargs) -> dict:
        value = int(amount * 100)
        order = self.client.order.create({
            "amount": value,
            "currency": currency,
            "receipt": order_id,
            "payment_capture": 1,
        })
        return {
            "order_id": order_id,
            "transaction_id": order.get("id"),
            "amount": amount,
            "currency": currency,
            "status": "created",
            "metadata": order,
        }

    def verify_payment(self, order_id: str, transaction_id: str, **kwargs) -> dict:
        payment = self.client.payment.fetch(transaction_id)
        status = "completed" if payment.get("status") == "captured" else "pending"
        return {
            "order_id": order_id,
            "transaction_id": transaction_id,
            "status": status,
            "metadata": payment,
        }

    def refund(self, order_id: str, transaction_id: str, amount: float, **kwargs) -> dict:
        value = int(amount * 100)
        refund = self.client.payment.refund(transaction_id, {"amount": value})
        return {
            "order_id": order_id,
            "transaction_id": transaction_id,
            "status": "refunded",
            "amount": amount,
            "metadata": refund,
        }
