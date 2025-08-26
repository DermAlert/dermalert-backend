from django.db import models
from django.conf import settings

from profile_forms.models.base_form import BaseForm
from profile_forms.enums.lifestyle_risk import (
    LongPeriodsPosture,
    YesNo,
    SmokingStatus,
)


class LifestyleRisk(BaseForm):
    """Risk and lifestyle factors form (singleton per user)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lifestyle_risk",
    )

    long_periods_posture = models.CharField(
        max_length=30, choices=LongPeriodsPosture.choices, default=LongPeriodsPosture.NO
    )
    leg_foot_trauma = models.CharField(
        max_length=5, choices=YesNo.choices, default=YesNo.NO
    )
    smoking = models.CharField(
        max_length=20, choices=SmokingStatus.choices, default=SmokingStatus.NEVER_SMOKED
    )
    physical_activity = models.CharField(
        max_length=5, choices=YesNo.choices, default=YesNo.NO
    )

    def __str__(self) -> str:
        return f"Lifestyle risk – {self.user}"
