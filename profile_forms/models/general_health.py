from core.models import BaseModel
from profile_forms.models.base_form import BaseForm
from profile_forms.enums.general_health import PhysicalActivityFrequency
from django.db import models
from django.conf import settings


class GeneralHealth(BaseForm):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="general_health",
    )
    chronic_diseases = models.ManyToManyField(
        "ChronicDisease",
        blank=True,
        related_name="patients",
    )
    medicines = models.ManyToManyField(
        "Medicine",
        blank=True,
        related_name="patients",
    )
    allergies = models.ManyToManyField(
        "Allergy",
        blank=True,
        related_name="patients",
    )
    surgeries = models.TextField(
        blank=True,
        verbose_name="Surgeries",
        help_text="List any surgeries you have had, including dates and details.",
    )
    physical_activity_frequency = models.CharField(
        max_length=50,
        choices=PhysicalActivityFrequency.choices,
        default=PhysicalActivityFrequency.NEVER,
        verbose_name="Physical Activity Frequency",
        help_text="How often do you engage in physical activity?",
    )

    def __str__(self):
        return f"General health – {self.user}"


class _BaseListedItem(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name


class ChronicDisease(_BaseListedItem):
    pass


class Medicine(_BaseListedItem):
    pass


class Allergy(_BaseListedItem):
    pass
