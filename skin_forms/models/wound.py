from skin_forms.models.base_form import SkinForms, models
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

    # Wound dimensions
    height_mm = models.IntegerField()
    width_mm = models.IntegerField()

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
    increased_pain = models.BooleanField()
    perilesional_erythema = models.BooleanField()
    perilesional_edema = models.BooleanField()
    heat_or_warm_skin = models.BooleanField()
    increased_exudate = models.BooleanField()
    purulent_exudate = models.BooleanField()
    friable_tissue = models.BooleanField()
    stagnant_wound = models.BooleanField()
    biofilm_compatible_tissue = models.BooleanField()
    odor = models.BooleanField()
    hypergranulation = models.BooleanField()
    wound_size_increase = models.BooleanField()
    satallite_lesions = models.BooleanField()
    grayish_wound_bed = models.BooleanField()

    # Total score for the wound
    total_score = models.IntegerField()

    def __str__(self):
        return f"Wound {self.id} with total score {self.total_score}"

    class Meta:
        verbose_name = "Wound"
        verbose_name_plural = "Wounds"
        indexes = [
            models.Index(fields=["id"]),
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

        item1 = LesionDimension.get_points(float(self.height_mm), float(self.width_mm))
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
