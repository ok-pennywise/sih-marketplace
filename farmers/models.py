from datetime import datetime
from typing import Optional
from django.db import models

from model_utils import aware_utcnow


class Farmer(models.Model):
    full_name: str = models.CharField(max_length=256)
    farm_name: Optional[str] = models.CharField(max_length=255, blank=True, null=True)

    address: str = models.CharField(max_length=255)
    description: Optional[str] = models.TextField(blank=True, null=True)

    date_of_birth: datetime = models.DateTimeField()
    date_joined: datetime = models.DateTimeField(editable=False, default=aware_utcnow)
