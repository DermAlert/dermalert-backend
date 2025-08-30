from skin_forms.models.base_form import SkinForms, models


class Cancer(SkinForms):
    """
    Model representing a cancer.
    """

    height_mm = models.IntegerField()
    width_mm = models.IntegerField()
    depth_injury = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Cancer"
        verbose_name_plural = "Cancers"
        indexes = [
            models.Index(fields=["id"]),
        ]
