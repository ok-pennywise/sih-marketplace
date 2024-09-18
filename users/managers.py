from datetime import date
from typing import TYPE_CHECKING, Optional
from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import BaseUserManager

if TYPE_CHECKING:
    from .models import User


class UserManager(BaseUserManager):
    def create_user(
        self,
        email: str,
        phone: str,
        password: str,
        date_of_birth: date,
        user_type: str = "buyer",
        farm_name: Optional[str] = None,
        *args,
        **kwargs
    ) -> "User":
        if not email:
            raise ValueError("The Email field must be set")
        if not phone:
            raise ValueError("The Phone field must be set")
        if not date_of_birth:
            raise ValueError("The Date of Birth field must be set")

        # Normalize email
        email = self.normalize_email(email)

        # Create and save the user
        user = self.model(
            email=email,
            phone=phone,
            date_of_birth=date_of_birth,
            user_type=user_type,
            farm_name=farm_name,
            **kwargs
        )
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        phone: str,
        password: str,
        date_of_birth: date,
        user_type: str = "admin",
        farm_name: Optional[str] = None,
        *args,
        **kwargs
    ) -> "User":
        """
        Create and return a superuser with an email, phone, and password.
        """
        extra_fields = {
            "is_staff": True,
            "is_superuser": True,
        }
        return self.create_user(
            email=email,
            phone=phone,
            password=password,
            date_of_birth=date_of_birth,
            user_type=user_type,
            farm_name=farm_name,
            **extra_fields
        )
