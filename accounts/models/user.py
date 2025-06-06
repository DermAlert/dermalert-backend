from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel
from dermalert import settings


class User(AbstractUser, BaseModel):
    username = None
    cpf = models.CharField(
        _("CPF"),
        max_length=11,
        help_text=_(""),
        error_messages={
            "unique": _("A user with that cpf already exists."),
        },
        unique=True,
        blank=False,
        null=False,
    )

    # unique=false because people who don't have email and use their relatives'
    email = models.EmailField(_("Email Address"), blank=True, unique=False)

    first_name = models.CharField(_("First Name"), max_length=150, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=150, blank=True)

    address = models.ForeignKey(
        "address.Address",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Address"),
    )

    USERNAME_FIELD = settings.USERNAME_FIELD
