from django.conf import settings
from .base import BasePaymentProvider
from .razorpay_provider import RazorpayPaymentProvider
from .stripe_provider import StripePaymentProvider
from ..exceptions.payment_exceptions import InvalidProviderError


class PaymentProviderFactory:
    """Factory to choose provider implementation dynamically."""

    PROVIDERS = {
        "razorpay": RazorpayPaymentProvider,
        "stripe": StripePaymentProvider,
    }

    @staticmethod
    def get_provider(provider_name: str = None) -> BasePaymentProvider:
        configured_default = getattr(settings, "PAYMENT_GATEWAY_DEFAULT_PROVIDER", None)
        chosen_name = provider_name or configured_default
        if not chosen_name:
            raise InvalidProviderError("No payment provider configured.")

        normalized = chosen_name.lower()
        provider_class = PaymentProviderFactory.PROVIDERS.get(normalized)

        if not provider_class:
            raise InvalidProviderError(f"Unsupported provider: {chosen_name}")

        return provider_class()
