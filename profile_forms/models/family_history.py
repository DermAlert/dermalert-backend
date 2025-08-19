from core.models import BaseListedItem
from django.db import models
from .base_form import BaseForm

class FamilyHistory(BaseForm):
    family_history = models.ManyToManyField(
        "Parents",
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
    
class Parents(BaseListedItem):
    """Model to represent parents in the family history."""
    pass

class InjuriesTreatment(BaseListedItem):
    """Model to represent treatment for injuries."""
    pass