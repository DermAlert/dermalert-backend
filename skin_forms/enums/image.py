from django.db import models
from django.utils.translation import gettext_lazy as _


class ImageType(models.TextChoices):
    """
    Enum for image types.
    """

    DERMOSCOPIC = "dermoscopic", _("Dermoscopy")
    PHOTOGRAPHIC = "photographic", _("Photographic")
