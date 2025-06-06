from django.db import models
from django.utils.translation import gettext_lazy as _


class PermissionRole(models.TextChoices):
    """
    Enum representing the permission roles in the system.
    """

    SUPERVISOR = "supervisor", _("Supervisor")
    TECHNICIAN = "technician", _("Technician")
