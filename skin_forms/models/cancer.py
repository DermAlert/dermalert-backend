from skin_forms.models.base_form import SkinForms, models
from skin_forms.enums.cancer import (
    Asymmetry,
    Border,
    ColorVariation,
    Diameter,
    Evolution,
)
from skin_conditions.models import SkinCondition


class Cancer(SkinForms):
    """ABCDE questionnaire for suspicious skin lesion."""

    skin_condition = models.ForeignKey(
        SkinCondition,
        on_delete=models.CASCADE,
        related_name="cancer_forms",
    )

    asymmetry = models.CharField(
        max_length=32, choices=Asymmetry.choices, default=Asymmetry.SYMMETRIC
    )
    border = models.CharField(
        max_length=32, choices=Border.choices, default=Border.REGULAR_WELL_DEFINED
    )
    color_variation = models.CharField(
        max_length=32,
        choices=ColorVariation.choices,
        default=ColorVariation.SINGLE_COLOR,
    )
    diameter = models.CharField(
        max_length=32, choices=Diameter.choices, default=Diameter.UNDER_6MM
    )
    evolution = models.CharField(
        max_length=32, choices=Evolution.choices, default=Evolution.NO_CHANGES
    )

    class Meta:
        verbose_name = "ABCDE cancer form"
        verbose_name_plural = "ABCDE cancer forms"
        indexes = [models.Index(fields=["id"]), models.Index(fields=["skin_condition"])]
