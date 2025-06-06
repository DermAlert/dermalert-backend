from django.db import models


class PhysicalActivityFrequency(models.TextChoices):
    DAILY = "daily", "Daily"
    THREE_TO_FIVE_TIMES_A_WEEK = "3-5 times a week", "3-5 times a week"
    ONE_TO_TWO_TIMES_A_WEEK = "1-2 times a week", "1-2 times a week"
    OCCASIONALLY = "occasionally", "Occasionally"
    NEVER = "never", "Never"
