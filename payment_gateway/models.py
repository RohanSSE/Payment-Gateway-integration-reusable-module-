from django.db import models


class PaymentRecord(models.Model):
    STATUS_CHOICES = [
        ("created", "Created"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    order_id = models.CharField(max_length=128)
    transaction_id = models.CharField(max_length=128, blank=True, null=True)
    payment_id = models.CharField(max_length=128, blank=True, null=True)
    signature = models.TextField(blank=True, null=True)
    provider = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="INR")
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="created")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("order_id", "provider")
        indexes = [models.Index(fields=["provider", "status"])]

    def __str__(self):
        return f"{self.provider} {self.order_id} {self.status}"
