from django.db import models
from django.conf import settings

from profile_forms.models.base_form import BaseForm
from profile_forms.enums.cancer_research import HowLong
from profile_forms.enums.clinical_history import YesNoUnknown
from profile_forms.enums.current_ulcer_info import UlcerTreatmentPlace


class CurrentUlcerInfo(BaseForm):
    """Information about the current ulcer (singleton per user)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="current_ulcer_info",
    )

    how_long = models.CharField(
        max_length=30, choices=HowLong.choices, default=HowLong.LESS_THAN_ONE_MONTH
    )
    treated_elsewhere = models.CharField(
        max_length=20,
        choices=UlcerTreatmentPlace.choices,
        default=UlcerTreatmentPlace.NONE,
    )
    used_antibiotics = models.CharField(
        max_length=20, choices=YesNoUnknown.choices, default=YesNoUnknown.NO
    )

    def __str__(self) -> str:
        return f"Current ulcer info – {self.user}"
