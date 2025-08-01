from core.models import BaseModel
from django.conf import settings
from django.db import models
from accounts.enums.gender import Gender


class Patient(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_profile",
        primary_key=True,
    )
    sus_number = models.CharField(max_length=15, unique=True)
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(
        max_length=1, choices=Gender.choices, default=Gender.NOT_INFORMED
    )
    other_gender = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField()
