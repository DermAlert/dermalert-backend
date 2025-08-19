from core.models import BaseModel
from django.db import models
from django.conf import settings


class BaseForm(BaseModel):
    """
    Base model for forms to store common information.
    """

    id = models.AutoField(primary_key=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile_forms",
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True
