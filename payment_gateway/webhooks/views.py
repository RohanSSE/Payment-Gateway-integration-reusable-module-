import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from . import signals

logger = logging.getLogger(__name__)


class BaseWebhookAPIView(APIView):
    """Common webhook behavior for all providers."""

    def post(self, request, *args, **kwargs):
        raise NotImplementedError


class RazorpayWebhookAPIView(BaseWebhookAPIView):
    def post(self, request, *args, **kwargs):
        payload = request.data
        logger.info("Razorpay webhook received: %s", payload)
        # Optional: verify signature in headers (X-Razorpay-Signature)
        # in production we should verify with settings.PAYMENT_GATEWAY_PROVIDERS["razorpay"]["webhook_secret"]
        try:
            signals.razorpay_webhook_received.send(sender=self.__class__, payload=payload)
        except Exception:
            logger.exception("Error handling Razorpay webhook")
            return Response({"status": "error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"status": "ok", "message": "razorpay webhook received"}, status=status.HTTP_200_OK)


class StripeWebhookAPIView(BaseWebhookAPIView):
    def post(self, request, *args, **kwargs):
        payload = request.data
        logger.info("Stripe webhook received: %s", payload)
        # Optional: verify signature header with stripe.Webhook.construct_event
        try:
            signals.stripe_webhook_received.send(sender=self.__class__, payload=payload)
        except Exception:
            logger.exception("Error handling Stripe webhook")
            return Response({"status": "error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"status": "ok", "message": "stripe webhook received"}, status=status.HTTP_200_OK)
