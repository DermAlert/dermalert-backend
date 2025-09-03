from core.models import BaseModel
from django.db import models
from ..enums import BodySite, SkinConditionType
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
    type = models.CharField(
        max_length=128,
        choices=SkinConditionType.choices,
        verbose_name="Skin Condition Type",
        default=SkinConditionType.WOUND,
    )
