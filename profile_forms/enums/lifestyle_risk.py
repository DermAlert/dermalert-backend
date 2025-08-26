from django.db import models


class LongPeriodsPosture(models.TextChoices):
    STANDING_LONG_HOURS = "STANDING_LONG_HOURS", "Yes, standing for many hours"
    SITTING_LONG_HOURS = "SITTING_LONG_HOURS", "Yes, sitting for many hours"
    NO = "NO", "No"


class YesNo(models.TextChoices):
    YES = "YES", "Yes"
    NO = "NO", "No"


class SmokingStatus(models.TextChoices):
    CURRENT_SMOKER = "CURRENT_SMOKER", "Yes, currently"
    FORMER_SMOKER = "FORMER_SMOKER", "I used to smoke, but quit"
    NEVER_SMOKED = "NEVER_SMOKED", "Never smoked"
