from django.db import models
from django.utils.translation import gettext_lazy as _


class SkinCondition(models.Model):
    """
    Model representing a skin condition.
    """

    class Location(models.TextChoices):
        HEAD = "head", "Head"
        NECK = "neck", "Neck"
        BACK = "back", "Back"
        CHEST = "chest", "Chest"
        ABDOMEN = "abdomen", "Abdomen"
        ARM = "arm", "Arm"
        LEG = "leg", "Leg"
        HAND = "hand", "Hand"
        FOOT = "foot", "Foot"

    id = models.UUIDField(primary_key=True, editable=False)
    user_id = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    location = models.CharField(
        _("skin_location"), max_length=50, choices=Location.choices
    )
    reference = models.CharField(_("reference"), max_length=255, null=True, blank=True)
    day_discovery = models.DateField()

    def __str__(self):
        return f"SkinCondition {self.id} for User {self.user_id}"
