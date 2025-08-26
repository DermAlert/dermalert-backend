from django.db import models
from django.conf import settings

from profile_forms.models.base_form import BaseForm
from profile_forms.enums.clinical_history import YesNoUnknown


class FamilyVascularHistory(BaseForm):
    """Family history about vascular issues (singleton per user)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="family_vascular_history",
    )

    family_leg_ulcers = models.CharField(
        max_length=20, choices=YesNoUnknown.choices, default=YesNoUnknown.NO
    )
    family_varicose_or_circulatory = models.CharField(
        max_length=20, choices=YesNoUnknown.choices, default=YesNoUnknown.NO
    )

    def __str__(self) -> str:
        return f"Family vascular history – {self.user}"
