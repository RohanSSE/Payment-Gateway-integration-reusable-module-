from django.urls import path
from .views import CreatePaymentAPIView, VerifyPaymentAPIView, RefundPaymentAPIView
from .webhooks.views import RazorpayWebhookAPIView, StripeWebhookAPIView

urlpatterns = [
    path("create/", CreatePaymentAPIView.as_view(), name="payment-create"),
    path("verify/", VerifyPaymentAPIView.as_view(), name="payment-verify"),
    path("refund/", RefundPaymentAPIView.as_view(), name="payment-refund"),
    path("webhook/razorpay/", RazorpayWebhookAPIView.as_view(), name="razorpay-webhook"),
    path("webhook/stripe/", StripeWebhookAPIView.as_view(), name="stripe-webhook"),
]
