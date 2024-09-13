from django.db import models

from farmers.models import Farmer
from model_utils import generate_id


class Category(models.Model):
    name: str = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    id: str = models.CharField(max_length=20, default=generate_id)

    farmer: Farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)

    name: str = models.CharField(max_length=256)
    description: str = models.TextField(blank=True, null=True)

    price: float = models.DecimalField(max_digits=10, decimal_places=2)

    min_quantity: int = models.IntegerField(default=1)
    max_quantity: int = models.IntegerField(default=10000)

    category: str = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )


class ProductImage(models.Model):
    product: Product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    url: str = models.ImageField(upload_to="product_images/")
