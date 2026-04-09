class PaymentProviderError(Exception):
    """Generic payment provider error."""


class PaymentNotFoundError(PaymentProviderError):
    """Payment record not found."""


class InvalidProviderError(PaymentProviderError):
    """Unknown or invalid payment provider."""
