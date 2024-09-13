from typing import Optional
from django.db import models
from model_utils import aware_utcnow
from datetime import datetime
from django.core.exceptions import ValidationError


class Buyer(models.Model):
    full_name: str = models.CharField(max_length=256)

    email: str = models.CharField(max_length=256, blank=True, null=True)
    phone: str = models.CharField(max_length=20, blank=True, null=True)

    date_joined: datetime = models.DateTimeField(editable=False, default=aware_utcnow)

    def save(self, *a, **kw) -> None:
        if not (self.email or self.phone):
            raise ValidationError("Either phone or email is required")


class Address(models.Model):
    buyer: Buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    title: str = models.CharField(max_length=100)

    street_address: str = models.CharField(
        max_length=255
    )  # Street address, e.g., '123 Main St'
    city: str = models.CharField(max_length=100)  # City, e.g., 'Springfield'
    state_or_region: str = models.CharField(
        max_length=100
    )  # State or province, e.g., 'IL'
    postal_code: str = models.CharField(max_length=20)  # Postal code, e.g., '62704'
    country: str = models.CharField(max_length=100)

    landmark: Optional[str] = models.CharField(max_length=100)
