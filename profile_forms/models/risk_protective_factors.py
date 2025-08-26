from django.db import models
from django.conf import settings
from .base_form import BaseForm
from profile_forms.enums.risk_protective_factors import (
    SunExposurePeriod,
    SunBurnHistory,
    UVProtectionSPF,
    CheckupsFrequency,
)


class RiskProtectiveFactors(BaseForm):
    # Singleton per user
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="risk_protective_factors",
    )

    sun_exposure_period = models.CharField(
        max_length=40, choices=SunExposurePeriod.choices
    )
    sun_burn = models.CharField(max_length=40, choices=SunBurnHistory.choices)
    uv_protection = models.CharField(max_length=40, choices=UVProtectionSPF.choices)
    hat_use = models.BooleanField(default=False)
    artifitial_tan = models.BooleanField(default=False)
    checkups_frequency = models.CharField(
        max_length=40, choices=CheckupsFrequency.choices
    )
    cancer_campaigns = models.BooleanField(default=False)

    def __str__(self):
        return f"RiskProtectiveFactors – {self.user}"
