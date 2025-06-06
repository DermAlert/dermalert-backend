from core.models import BaseModel, models
from accounts.enums.permission_role import PermissionRole


class InviteWork(BaseModel):
    """
    Model representing an invite code.
    """

    hash = models.CharField(max_length=255, unique=True)
    email = models.EmailField()

    expires_at = models.DateTimeField(null=True, blank=True)

    permission_role = models.CharField(
        max_length=15,
        choices=PermissionRole.choices,
        default=PermissionRole.TECHNICIAN,
        verbose_name="Permission Role",
    )

    health_unit_code = models.ForeignKey(
        "health_unit.HealthUnit",
        on_delete=models.CASCADE,
        related_name="invite_codes",
        verbose_name="Health Unit",
    )

    start_date_work = models.DateTimeField(null=True, blank=True)
    end_date_work = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Invite Code"
        verbose_name_plural = "Invite Codes"

    def __str__(self):
        return self.hash
