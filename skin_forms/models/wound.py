from skin_forms.models.base_form import SkinForms, models
from skin_conditions.models import SkinCondition
from skin_forms.enums.wound import (
    WoundEdges,
    WoundBedTissue,
    DepthOfTissueInjury,
    ExudateType,
    LesionDimension,
)


class Wound(SkinForms):
    """
    Model representing a wound.
    """

    # Parent relation (nested under a SkinCondition)
    skin_condition = models.ForeignKey(
        SkinCondition,
        on_delete=models.CASCADE,
        related_name="wounds",
    )

    # Wound dimensions (stored in millimeters, computed in cm for scoring)
    height_mm = models.PositiveIntegerField()
    width_mm = models.PositiveIntegerField()

    # Wound characteristics
    wound_edges = models.CharField(
        max_length=50, choices=WoundEdges.choices, default=WoundEdges.NO_EDGES
    )
    wound_bed_tissue = models.CharField(
        max_length=50,
        choices=WoundBedTissue.choices,
        default=WoundBedTissue.REGENERATED_SCARRED,
    )
    depth_of_tissue_injury = models.CharField(
        max_length=50,
        choices=DepthOfTissueInjury.choices,
        default=DepthOfTissueInjury.INTACT_SKIN,
    )
    exudate_type = models.CharField(
        max_length=50,
        choices=ExudateType.choices,
        default=ExudateType.DRY,
    )

    # Signs of infection
    increased_pain = models.BooleanField(default=False)
    perilesional_erythema = models.BooleanField(default=False)
    perilesional_edema = models.BooleanField(default=False)
    heat_or_warm_skin = models.BooleanField(default=False)
    increased_exudate = models.BooleanField(default=False)
    purulent_exudate = models.BooleanField(default=False)
    friable_tissue = models.BooleanField(default=False)
    stagnant_wound = models.BooleanField(default=False)
    biofilm_compatible_tissue = models.BooleanField(default=False)
    odor = models.BooleanField(default=False)
    hypergranulation = models.BooleanField(default=False)
    wound_size_increase = models.BooleanField(default=False)
    satallite_lesions = models.BooleanField(default=False)
    grayish_wound_bed = models.BooleanField(default=False)

    # Total score for the wound
    total_score = models.IntegerField(editable=False)

    def __str__(self):
        return f"Wound {self.id} with total score {self.total_score}"

    class Meta:
        verbose_name = "Wound"
        verbose_name_plural = "Wounds"
        indexes = [
            models.Index(fields=["id"]),
            models.Index(fields=["skin_condition"]),
        ]

    def save(self, *args, **kwargs):
        """
        Override the save method to calculate the total score before saving.
        """
        # Calculate the total score
        self.total_score = self.get_total_score()
        super().save(*args, **kwargs)

    def get_total_score(self) -> int:
        """Retorna a soma de todos os itens (1 a 6)."""
        # Convert stored dimensions from mm to cm for scoring
        height_cm = float(self.height_mm) / 10.0
        width_cm = float(self.width_mm) / 10.0
        item1 = LesionDimension.get_points(height_cm, width_cm)
        item2 = DepthOfTissueInjury.get_points(self.depth_of_tissue_injury)
        item3 = WoundEdges.get_points(self.wound_edges)
        item4 = WoundBedTissue.get_points(self.wound_bed_tissue)
        item5 = ExudateType.get_points(self.exudate_type)
        item6 = self.get_item6_points()
        total = item1 + item2 + item3 + item4 + item5 + item6
        return total

    def get_item6_points(self) -> int:
        """
        Retorna a soma dos pontos dos sinais de infecção/inflamação.
        Cada sinal tem 1 ponto.
        """

        fields = [
            "increased_pain",
            "perilesional_erythema",
            "perilesional_edema",
            "heat_or_warm_skin",
            "increased_exudate",
            "purulent_exudate",
            "friable_tissue",
            "stagnant_wound",
            "biofilm_compatible_tissue",
            "odor",
            "hypergranulation",
            "wound_size_increase",
            "satallite_lesions",
            "grayish_wound_bed",
        ]

        return sum(getattr(self, field) for field in fields)

    
