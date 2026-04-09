import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import PaymentRecord
from .serializers import (
    CreatePaymentSerializer,
    VerifyPaymentSerializer,
    RefundPaymentSerializer,
    PaymentRecordSerializer,
)
from .services.factory import PaymentProviderFactory
from .exceptions import PaymentProviderError, PaymentNotFoundError

logger = logging.getLogger(__name__)


class CreatePaymentAPIView(APIView):
    """API view to create a payment via provider factory and record it to DB."""

    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider_name = serializer.validated_data.get("provider")
        provider = PaymentProviderFactory.get_provider(provider_name)

        try:
            logger.info("Create payment request: %s", serializer.validated_data)
            data = provider.create_payment(
                order_id=serializer.validated_data["order_id"],
                amount=float(serializer.validated_data["amount"]),
                currency=serializer.validated_data["currency"],
            )

            payment = PaymentRecord.objects.update_or_create(
                order_id=data["order_id"],
                provider=provider_name or provider.__class__.__name__.lower().replace("paymentprovider", ""),
                defaults={
                    "transaction_id": data.get("transaction_id"),
                    "payment_id": data.get("payment_id"),
                    "amount": data.get("amount"),
                    "currency": data.get("currency"),
                    "status": data.get("status"),
                    "metadata": data.get("metadata", {}),
                },
            )[0]

            output = PaymentRecordSerializer(payment)
            return Response(output.data, status=status.HTTP_201_CREATED)

        except PaymentProviderError as exc:
            logger.error("Create payment failed for order %s: %s", serializer.validated_data.get("order_id"), exc, exc_info=True)
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            logger.exception("Unexpected error in create payment")
            detail = str(exc) if settings.DEBUG else "Internal server error"
            return Response({"detail": detail}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyPaymentAPIView(APIView):
    """API view to verify a payment status."""

    def post(self, request):
        serializer = VerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider_name = serializer.validated_data.get("provider")
        provider = PaymentProviderFactory.get_provider(provider_name)

        try:
            logger.info("Verify payment request: %s", serializer.validated_data)
            result = provider.verify_payment(
                order_id=serializer.validated_data["order_id"],
                transaction_id=serializer.validated_data["transaction_id"],
                payment_id=serializer.validated_data.get("payment_id"),
                signature=serializer.validated_data.get("signature"),
            )

            provider_key = provider_name or provider.__class__.__name__.lower().replace("paymentprovider", "")
            payment = get_object_or_404(PaymentRecord, order_id=result["order_id"], provider=provider_key)
            payment.status = "success" if result["status"] == "success" else "failed"
            payment.transaction_id = result["transaction_id"]
            payment.payment_id = serializer.validated_data.get("payment_id") or result.get("payment_id") or result["transaction_id"]
            payment.signature = serializer.validated_data.get("signature")
            payment.metadata = result.get("metadata", {})
            payment.save()

            output = PaymentRecordSerializer(payment)
            return Response(output.data, status=status.HTTP_200_OK)

        except PaymentNotFoundError as exc:
            logger.warning("Verify payment not found: %s", serializer.validated_data)
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except PaymentProviderError as exc:
            logger.error("Verify payment failed for order %s: %s", serializer.validated_data.get("order_id"), exc, exc_info=True)
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            logger.exception("Unexpected error in verify payment")
            detail = str(exc) if settings.DEBUG else "Internal server error"
            return Response({"detail": detail}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RefundPaymentAPIView(APIView):
    """API view to refund an existing payment."""

    def post(self, request):
        serializer = RefundPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider_name = serializer.validated_data.get("provider")
        provider = PaymentProviderFactory.get_provider(provider_name)

        try:
            logger.info("Refund payment request: %s", serializer.validated_data)
            result = provider.refund(
                order_id=serializer.validated_data["order_id"],
                transaction_id=serializer.validated_data.get("transaction_id", ""),
                payment_id=serializer.validated_data.get("payment_id"),
                amount=float(serializer.validated_data["amount"]),
            )

            provider_key = provider_name or provider.__class__.__name__.lower().replace("paymentprovider", "")
            payment = get_object_or_404(PaymentRecord, order_id=result["order_id"], provider=provider_key)
            payment.status = result["status"]
            payment.amount = result["amount"]
            payment.payment_id = result.get("payment_id") or payment.payment_id or result.get("transaction_id")
            payment.metadata = result.get("metadata", {})
            payment.save()

            output = PaymentRecordSerializer(payment)
            return Response(output.data, status=status.HTTP_200_OK)

        except PaymentProviderError as exc:
            logger.error("Refund payment failed for order %s: %s", serializer.validated_data.get("order_id"), exc, exc_info=True)
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            logger.exception("Unexpected error in refund payment")
            detail = str(exc) if settings.DEBUG else "Internal server error"
            return Response({"detail": detail}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
