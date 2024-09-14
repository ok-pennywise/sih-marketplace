from datetime import datetime, date
from django.db import models

from model_utils import aware_utcnow, generate_id
from django.contrib.auth.hashers import check_password
from . import managers


# Create your models here.
class User(models.Model):
    id: str = models.CharField(max_length=20, default=generate_id, primary_key=True)

    email: str = models.CharField(max_length=256, unique=True)
    phone: str = models.CharField(max_length=20, unique=True)

    full_name: str = models.CharField(max_length=256)

    date_joined: datetime = models.DateTimeField(default=aware_utcnow, editable=False)

    password: str = models.CharField(max_length=128)

    BUYER: str = "buyer"
    FARMER: str = "farmer"

    USER_TYPE_CHOICES: tuple[tuple[str, str]] = ((BUYER, "Buyer"), (FARMER, "Farmer"))

    user_type: str = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default=BUYER
    )

    date_of_birth: date = models.DateField()
    farm_name: str = models.CharField(max_length=256, blank=True, null=True)

    def verify_password(self, password: str) -> bool:
        return check_password(password, self.password)

    objects = managers.UserManager()


class Address(models.Model):
    id: str = models.CharField(max_length=20, default=generate_id, primary_key=True)

    user: User = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="addresses"
    )
    name: str = models.CharField(max_length=20)
    street_address: str = models.CharField(max_length=255)
    city: str = models.CharField(max_length=100)
    state: str = models.CharField(max_length=100)
    postal_code: str = models.CharField(max_length=20)
    country: str = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state} {self.postal_code}, {self.country}"
