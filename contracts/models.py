from datetime import datetime, timedelta
from django.db import models


from model_utils import aware_utcnow, generate_id
from products.models import Product
from users.models import User

from django.core.exceptions import ValidationError


def _default_contract_end_date() -> datetime:
    return aware_utcnow() + timedelta(days=365)


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

    product: Product = models.ForeignKey(Product, on_delete=models.CASCADE)

    start_date: datetime = models.DateTimeField(
        default=aware_utcnow
    )  # Contract start date
    end_date = models.DateTimeField(default=_default_contract_end_date)

    payment_terms: str = models.TextField(
        blank=True, null=True
    )  # Details of payment terms
    delivery_terms: str = models.TextField(blank=True, null=True)

    UPI_PAYMENT: str = "upi"
    COD_PAYMENT: str = "cod"
    CREDIT_PAYMENT: str = "credit"
    DEBIT_PAYMENT: str = "debit"

    PAYMENT_METHOD_CHOICES: tuple[tuple[str, str]] = (
        (UPI_PAYMENT, "UPI"),
        (COD_PAYMENT, "Cash on delivery"),
        (CREDIT_PAYMENT, "Credit card"),
        (DEBIT_PAYMENT, "Debit card"),
    )

    payment_method: str = models.CharField(
        max_length=10, choices=PAYMENT_METHOD_CHOICES, default="upi"
    )

    quantity: int = models.PositiveIntegerField()
    price_per_unit: float = models.DecimalField(max_digits=10, decimal_places=2)
    total_price: float = models.DecimalField(max_digits=12, decimal_places=2)

    discount: float = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    terms_and_conditions: str = models.TextField()

    is_active: bool = models.BooleanField(default=True)

    def clean(self) -> None:
        if self.product.max_quantity < self.quantity < self.product.min_quantity:
            raise ValidationError(
                f"Minimum of {self.product.min_quantity} and at max {self.product.max_quantity}"
            )
        return super().clean()

    def save(self, *a, **kw) -> None:
        self.price_per_unit = self.product.price
        self.total_price = self.price_per_unit * self.quantity
        if self.discount > 0:
            self.total_price(self.total_price / 100) * self.discount
        super().save(*a, **kw)
