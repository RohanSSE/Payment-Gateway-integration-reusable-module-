from django.apps import AppConfig


class PaymentGatewayConfig(AppConfig):
    name = "payment_gateway"
    verbose_name = "Payment Gateway"

    def ready(self):
        # Place for signal registration in future
        pass
