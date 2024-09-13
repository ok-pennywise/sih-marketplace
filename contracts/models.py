from datetime import datetime
from django.db import models


from model_utils import aware_utcnow, generate_id
from users.models import User


# Create your models here.
class Contract(models.Model):

    id: str = models.CharField(max_length=20, default=generate_id, primary_key=True)

    buyer: User = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="buyer_contracts",
        editable=False,
    )
    farmer: User = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="farmer_contracts",
        editable=False,
    )

    quantity: str = models.IntegerField(default=0)
    description: str = models.TextField(blank=True, null=True)

    price: float = models.DecimalField(max_digits=10, decimal_places=2)

    start_date = models.DateTimeField(default=aware_utcnow)  # Contract start date
    end_date = models.DateTimeField(null=True, blank=True)

    payment_terms: str = models.TextField(
        blank=True, null=True
    )  # Details of payment terms
    delivery_terms: str = models.TextField(blank=True, null=True)

    PAYMENT_METHOD_CHOICES: tuple[tuple[str, str]] = (
        ("upi", "UPI"),
        ("cod", "Cash on delivery"),
        ("credit", "Credit card"),
        ("debit", "Debit card"),
    )

    payment_method: str = models.CharField(
        max_length=10, choices=PAYMENT_METHOD_CHOICES, default="upi"
    )

    created_on: datetime = models.DateTimeField(default=aware_utcnow, editable=False)
