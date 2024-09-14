from ninja import ModelSchema, Schema

from users.models import Address, User


class AddressInOut(ModelSchema):
    class Meta:
        model = Address
        exclude = ("user",)


class UserIn(ModelSchema):
    class Meta:
        model = User
        fields = (
            "email",
            "phone",
            "password",
            "user_type",
            "date_of_birth",
            "farm_name",
        )


class UserOut(ModelSchema):
    addresses: list[AddressInOut]

    class Meta:
        model = User
        fields = (
            "email",
            "phone",
            "user_type",
            "date_of_birth",
            "farm_name",
        )


class LoginIn(Schema):
    query: str
    password: str
