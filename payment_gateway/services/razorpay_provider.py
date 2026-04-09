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
        except razorpay.errors.BadRequestError as exc:
            raise PaymentProviderError("Invalid request") from exc
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
        payment_id = kwargs.get("payment_id") or transaction_id
        signature = kwargs.get("signature")

        if not payment_id:
            raise PaymentProviderError("payment_id is required to verify Razorpay payment.")

        if signature:
            try:
                self.client.utility.verify_payment_signature({
                    "razorpay_order_id": order_id,
                    "razorpay_payment_id": payment_id,
                    "razorpay_signature": signature,
                })
            except Exception as exc:
                raise PaymentProviderError("Invalid Razorpay payment signature.") from exc

        try:
            payment = self.client.payment.fetch(payment_id)
        except razorpay.errors.BadRequestError as exc:
            raise PaymentProviderError("Invalid request") from exc
        except Exception as exc:
            raise PaymentProviderError(str(exc)) from exc

        fetched_order_id = payment.get("order_id")
        if fetched_order_id and fetched_order_id != order_id:
            raise PaymentProviderError("Payment does not belong to the provided order_id.")

        status = "success" if payment.get("status") == "captured" else "failed"
        return {
            "order_id": order_id,
            "transaction_id": payment_id,
            "payment_id": payment_id,
            "status": status,
            "metadata": payment,
        }

    def refund(self, order_id: str, transaction_id: str, amount: float, **kwargs) -> dict:
        payment_id = kwargs.get("payment_id") or transaction_id
        value = int(amount * 100)
        if not payment_id:
            raise PaymentProviderError("payment_id is required to create Razorpay refund.")
        try:
            refund = self.client.payment.refund(payment_id, {"amount": value})
        except razorpay.errors.BadRequestError as exc:
            raise PaymentProviderError("Invalid request") from exc
        except Exception as exc:
            raise PaymentProviderError(str(exc)) from exc
        return {
            "order_id": order_id,
            "transaction_id": payment_id,
            "payment_id": payment_id,
            "status": "refunded",
            "amount": amount,
            "metadata": refund,
        }
