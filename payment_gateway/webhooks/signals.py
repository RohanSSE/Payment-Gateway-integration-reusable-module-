from django.dispatch import Signal

razorpay_webhook_received = Signal(providing_args=["payload"])
stripe_webhook_received = Signal(providing_args=["payload"])
