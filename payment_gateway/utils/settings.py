from django.conf import settings


def get_payment_gateway_settings():
    return {
        "default_provider": getattr(settings, "PAYMENT_GATEWAY_DEFAULT_PROVIDER", "razorpay"),
        "providers": getattr(settings, "PAYMENT_GATEWAY_PROVIDERS", {}),
    }
