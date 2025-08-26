from django.db import models
from django.conf import settings

from profile_forms.models.base_form import BaseForm
from profile_forms.enums.lifestyle_risk import YesNo


class CareAccessSupport(BaseForm):
    """Access to care and support related to wound (singleton per user)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="care_access_support",
    )

    has_dressings_available = models.CharField(
        max_length=5, choices=YesNo.choices, default=YesNo.NO
    )
    has_help_at_home = models.CharField(
        max_length=5, choices=YesNo.choices, default=YesNo.NO
    )

    def __str__(self) -> str:
        return f"Care access & support – {self.user}"
