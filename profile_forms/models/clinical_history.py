from django.db import models
from django.conf import settings

from profile_forms.models.base_form import BaseForm
from profile_forms.enums.clinical_history import (
    YesNoUnknown,
    CompressionStockingsUse,
)


class ClinicalHistory(BaseForm):
    """Singleton General Clinical History form per user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="clinical_history",
    )

    hypertension = models.CharField(
        max_length=20, choices=YesNoUnknown.choices, default=YesNoUnknown.NO
    )
    diabetes = models.CharField(
        max_length=20, choices=YesNoUnknown.choices, default=YesNoUnknown.NO
    )
    deep_vein_thrombosis = models.CharField(
        max_length=20, choices=YesNoUnknown.choices, default=YesNoUnknown.NO
    )
    chronic_venous_insufficiency = models.CharField(
        max_length=20, choices=YesNoUnknown.choices, default=YesNoUnknown.NO
    )
    compression_stockings_use = models.CharField(
        max_length=30,
        choices=CompressionStockingsUse.choices,
        default=CompressionStockingsUse.NEVER_USED,
    )

    def __str__(self) -> str:
        return f"Clinical history – {self.user}"
