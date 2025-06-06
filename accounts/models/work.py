from core.models import BaseModel, models
from django.conf import settings
from accounts.enums.permission_role import PermissionRole


class Work(BaseModel):
    """
    Model representing a work.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="works",
        verbose_name="User",
    )

    health_unit = models.ForeignKey(
        "health_unit.HealthUnit",
        on_delete=models.CASCADE,
        related_name="works",
        verbose_name="Health Unit",
    )

    permission_role = models.CharField(
        max_length=15,
        choices=PermissionRole.choices,
        default=PermissionRole.TECHNICIAN,
        verbose_name="Permission Role",
    )

    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        verbose_name = "Work"
        verbose_name_plural = "Works"

    def __str__(self):
        return f"{self.user} - {self.health_unit}"
