from datetime import date
from django.core.exceptions import ValidationError
from django.db.models import Q
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

    start_date = models.DateField(default=date.today)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Work"
        verbose_name_plural = "Works"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "health_unit"],
                condition=Q(is_active=True, is_deleted=False),
                name="accounts_work_unique_active_assignment",
            ),
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(
                    permission_role=PermissionRole.SUPERVISOR,
                    is_active=True,
                    is_deleted=False,
                ),
                name="accounts_work_unique_active_supervisor",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.health_unit}"

    def clean(self):
        super().clean()

        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date must be after start date."})
