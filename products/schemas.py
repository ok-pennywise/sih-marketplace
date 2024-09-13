from ninja import ModelSchema

from products.models import Product, ProductImage


class ProductImageOut(ModelSchema):
    class Meta:
        model = ProductImage
        fields = ("url",)


class ProductOut(ModelSchema):
    product_images: list[ProductImageOut]

    class Meta:
        model = Product
        fields = "__all__"
