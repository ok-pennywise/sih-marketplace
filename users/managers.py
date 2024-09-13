from datetime import date
from typing import TYPE_CHECKING, Optional
from django.db import models
from django.contrib.auth.hashers import make_password

if TYPE_CHECKING:
    from .models import User


class UserManager(models.Manager):
    def create(
        self,
        email: str,
        phone: str,
        password: str,
        date_of_birth: date,
        user_type: str = "buyer",
        farm_name: Optional[str] = None,
        *a,
        **kw
    ) -> "User":
        user: "User" = self.model(
            email=email,
            phone=phone,
            date_of_birth=date_of_birth,
            user_type=user_type,
            farm_name=farm_name,
        )
        user.password = make_password(password=password)
        user.save()
        return user
