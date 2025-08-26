from core.models import BaseListedItem
from django.db import models
from .base_form import BaseForm
from django.conf import settings


class FamilyHistory(BaseForm):
    # Override BaseForm.user to avoid reverse name collision and keep singleton per user
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="family_history",
    )
    family_history = models.ManyToManyField(
        "Relatives",
        blank=True,
        related_name="cancer_forms",
    )
    family_history_types = models.ManyToManyField(
        "CancerTypes",
        blank=True,
        related_name="cancer_forms",
    )
    patient_cancer_type = models.ForeignKey(
        "CancerTypes",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_forms",
    )
    removed_injuries = models.BooleanField(
        default=False,
        verbose_name="Removed Injuries",
        help_text="Indicate if there are any removed injuries.",
    )
    injuries_treatment = models.ManyToManyField(
        "InjuriesTreatment",
        blank=True,
        related_name="family_history_forms",
    )


class CancerTypes(BaseListedItem):
    """Model to represent cancer types in the family history."""

    pass


class Relatives(BaseListedItem):
    """Model to represent relatives in the family history."""

    pass


class InjuriesTreatment(BaseListedItem):
    """Model to represent treatment for injuries."""

    pass
