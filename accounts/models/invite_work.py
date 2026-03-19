from core.models import BaseModel, models
from accounts.enums.permission_role import PermissionRole
from django.conf import settings


class InviteWork(BaseModel):
    """
    Model representing an invite code.
    """

    hash = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="invite_works",
    )
    name = models.CharField(max_length=255)
    cpf = models.CharField(max_length=11)
    email = models.EmailField()
    accepted_at = models.DateTimeField(null=True, blank=True)

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
