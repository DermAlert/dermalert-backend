from core.models import BaseModel
from django.db import models
from ..enums import BodySite
from django.conf import settings


class SkinCondition(BaseModel):
    """Model representing a skin condition with its location and description."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="skin_conditions",
    )
    location = models.CharField(
        max_length=128, choices=BodySite.choices, verbose_name="Body Site"
    )
    description = models.TextField(verbose_name="Description")
