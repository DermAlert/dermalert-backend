from core.models import BaseModel
from django.db import models


class Session(BaseModel):
    user_id = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
    )

    start = models.TimeField()
    end = models.TimeField()

    class Meta:
        verbose_name = "Session"
        verbose_name_plural = "Sessions"
