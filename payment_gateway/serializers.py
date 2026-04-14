from rest_framework import serializers
from .models import PaymentRecord


class CreatePaymentSerializer(serializers.Serializer):
    order_id = serializers.CharField(max_length=128)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(max_length=8, default="INR")
    provider = serializers.CharField(max_length=64, required=False)


class VerifyPaymentSerializer(serializers.Serializer):
    order_id = serializers.CharField(max_length=128)
    provider = serializers.CharField(max_length=64, required=False)
    transaction_id = serializers.CharField(max_length=128)


class RefundPaymentSerializer(serializers.Serializer):
    order_id = serializers.CharField(max_length=128)
    provider = serializers.CharField(max_length=64, required=False)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)


class PaymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRecord
        fields = "__all__"
