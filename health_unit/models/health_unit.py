from core.models import BaseModel, models


class HealthUnit(BaseModel):
    """
    Model representing a health unit.
    """

    name = models.CharField(max_length=255, unique=True)
    address = models.ForeignKey("address.Address", on_delete=models.PROTECT)
    email = models.EmailField()

    class Meta:
        verbose_name = "Health Unit"
        verbose_name_plural = "Health Units"

    def __str__(self):
        return self.name
