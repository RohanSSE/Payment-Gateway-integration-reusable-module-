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
    transaction_id = serializers.CharField(max_length=128, required=False)
    payment_id = serializers.CharField(max_length=128, required=False)
    signature = serializers.CharField(max_length=256, required=False)

    def validate(self, attrs):
        transaction_id = attrs.get("transaction_id") or attrs.get("payment_id")
        if not transaction_id:
            raise serializers.ValidationError({"transaction_id": ["This field is required."]})

        provider = (attrs.get("provider") or "").lower()
        if provider == "razorpay":
            errors = {}
            if not attrs.get("payment_id"):
                errors["payment_id"] = ["This field is required for Razorpay verification."]
            if not attrs.get("signature"):
                errors["signature"] = ["This field is required for Razorpay verification."]
            if errors:
                raise serializers.ValidationError(errors)

        attrs["transaction_id"] = transaction_id
        return attrs


class RefundPaymentSerializer(serializers.Serializer):
    order_id = serializers.CharField(max_length=128)
    provider = serializers.CharField(max_length=64, required=False)
    transaction_id = serializers.CharField(max_length=128, required=False)
    payment_id = serializers.CharField(max_length=128, required=False)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate(self, attrs):
        transaction_id = attrs.get("transaction_id") or attrs.get("payment_id")
        if not transaction_id:
            raise serializers.ValidationError({"transaction_id": ["This field is required."]})
        attrs["transaction_id"] = transaction_id
        return attrs


class PaymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRecord
        fields = "__all__"
