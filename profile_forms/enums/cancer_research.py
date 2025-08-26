from django.db import models


class HowLong(models.TextChoices):
    LESS_THAN_ONE_MONTH = "lt_1_month", "Less than 1 month"
    ONE_TO_THREE_MONTHS = "1_3_months", "1-3 months"
    THREE_TO_SIX_MONTHS = "3_6_months", "3-6 months"
    MORE_THAN_SIX_MONTHS = "gt_6_months", "More than 6 months"
