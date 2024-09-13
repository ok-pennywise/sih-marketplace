from datetime import datetime
from django.db import models

from model_utils import aware_utcnow, generate_id
from users.models import User


class Category(models.Model):
    name: str = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    id: str = models.CharField(max_length=20, default=generate_id, primary_key=True)

    created_on: datetime = models.DateTimeField(default=aware_utcnow)

    user: User = models.ForeignKey(User, on_delete=models.CASCADE)

    name: str = models.CharField(max_length=256)
    description: str = models.TextField(blank=True, null=True)

    price: float = models.DecimalField(max_digits=10, decimal_places=2)

    min_quantity: int = models.IntegerField(default=1)
    max_quantity: int = models.IntegerField(default=10000)

    stock: int = models.IntegerField(default=0)

    in_stock: bool = models.BooleanField(default=True)

    category: str = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )


class ProductImage(models.Model):
    id: str = models.CharField(max_length=20, default=generate_id, primary_key=True)
    product: Product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    url: str = models.ImageField(upload_to="product_images/")
