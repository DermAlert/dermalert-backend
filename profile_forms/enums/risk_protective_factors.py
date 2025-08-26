from django.db import models


class SunExposurePeriod(models.TextChoices):
    DAILY = "daily", "Daily"
    FEW_TIMES_PER_WEEK = "few_times_per_week", "A few times per week"
    OCCASIONALLY = "occasionally", "Occasionally"
    NO_EXPOSURE = "no_exposure", "Does not expose to the sun"


class SunBurnHistory(models.TextChoices):
    ONCE_TWICE = "once_twice", "1-2 times"
    THREE_TO_FIVE = "three_to_five", "3-5 times"
    MORE_THAN_FIVE = "more_than_five", "More than 5 times"
    NEVER = "never", "Never had"


class UVProtectionSPF(models.TextChoices):
    NONE = "none", "Does not use"
    SPF_15 = "spf_15", "SPF 15"
    SPF_30 = "spf_30", "SPF 30"
    SPF_50 = "spf_50", "SPF 50"
    SPF_70 = "spf_70", "SPF 70"
    SPF_100_PLUS = "spf_100_plus", "SPF 100 or more"


class CheckupsFrequency(models.TextChoices):
    ANNUALLY = "annually", "Annually"
    EVERY_SIX_MONTHS = "every_six_months", "Every 6 months"
    NOT_REGULARLY = "not_regularly", "Not regularly"
    OTHER = "other", "Other"
