from django.db import models


class YesNoUnknown(models.TextChoices):
    YES = "YES", "Yes"
    NO = "NO", "No"
    DONT_KNOW = "DONT_KNOW", "Don't know"


class CompressionStockingsUse(models.TextChoices):
    CURRENTLY = "CURRENTLY", "Yes, currently"
    USED_BUT_NOT_ANYMORE = "USED_BUT_NOT_ANYMORE", "Yes, but not anymore"
    NEVER_USED = "NEVER_USED", "Never used"
    DONT_KNOW_WHAT_IT_IS = "DONT_KNOW_WHAT_IT_IS", "Doesn't know what it is"
