from core.models import BaseModel
from django.db import models


class Diagnosis(BaseModel):
    """Model representing a skin condition diagnosis."""

    name = models.CharField(max_length=255, unique=True, verbose_name="Diagnosis Name")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Diagnosis"
        verbose_name_plural = "Diagnoses"
        ordering = ["name"]

    def __str__(self):
        return self.name
