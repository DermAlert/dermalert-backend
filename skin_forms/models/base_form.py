from core.models import BaseModel, models


class BaseForm(BaseModel):
    """
    Wound model to store wound information.
    """

    id = models.AutoField(primary_key=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True
