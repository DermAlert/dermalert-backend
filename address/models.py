from django.db import models
from core.models import BaseModel
from django.utils.translation import gettext_lazy as _


class Address(BaseModel):
    cep = models.CharField(_("CEP"), max_length=8)
    country = models.CharField(_("Country"), max_length=100)
    state = models.CharField(_("State"), max_length=100)
    city = models.CharField(_("City"), max_length=100)
    neighborhood = models.CharField(_("Neighborhood"), max_length=100)
    street = models.CharField(_("Street"), max_length=255)
    number = models.IntegerField(_("Number"))
    longitude = models.FloatField(_("Longitude"))
    latitude = models.FloatField(_("Latitude"))

    class Meta:
        indexes = [
            models.Index(fields=["cep", "number"], name="address_index"),
            models.Index(fields=["latitude", "longitude"], name="geolocation_index"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["cep", "number"], name="unique_address"),
        ]
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")

    def __str__(self):
        return f"{self.street}, {self.number} - {self.city}/{self.state}"
