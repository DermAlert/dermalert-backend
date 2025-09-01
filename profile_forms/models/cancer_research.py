from django.db import models
from django.conf import settings
from .base_form import BaseForm
from profile_forms.enums.cancer_research import HowLong


class CancerResearch(BaseForm):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cancer_research",
    )

    suspicious_moles = models.BooleanField(default=False)
    bleed_itch = models.BooleanField(default=False)
    how_long = models.CharField(max_length=20, choices=HowLong.choices)
    lesion_aspect = models.BooleanField(default=False)
    diagnosis = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"CancerResearch – {self.user}"
