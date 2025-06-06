from core.models import BaseModel
from django.db import models


class BaseForm(BaseModel):
    """
    Base model for forms to store common information.
    """

    id = models.AutoField(primary_key=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="profile_forms",
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True
