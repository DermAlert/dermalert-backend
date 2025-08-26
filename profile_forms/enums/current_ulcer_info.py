from django.db import models


class UlcerTreatmentPlace(models.TextChoices):
    HOSPITAL = "HOSPITAL", "Yes, at hospital"
    UBS = "UBS", "Yes, at UBS"
    OTHER = "OTHER", "Yes, at another place"
    NONE = "NONE", "No"
