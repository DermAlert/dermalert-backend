import os
import uuid
from core.models import BaseModel, models
from skin_forms.enums.image import ImageType
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


def images_upload_to(instance, filename):
    """
    Gera um path como:
      images/<model_name>/<form_id>/<uuid>.<ext>
    Exemplo: images/wound/42/3f1c2e9a-7b8c-4d1e-9a5b-1234abcd5678.png
    """
    base, ext = os.path.splitext(filename)
    ext = ext.lower()

    new_filename = f"{uuid.uuid4()}{ext}"

    # model name from content type (e.g., 'wound')
    model_name = (
        instance.content_type.model if getattr(instance, "content_type_id", None) else "skin_form"
    )

    # object id is the target form id
    target_id = getattr(instance, "object_id", None) or "unknown"

    return os.path.join("images", model_name, str(target_id), new_filename)


class Image(BaseModel):
    """
    Model representing an image attached to any SkinForm via Generic FK.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    skin_form = GenericForeignKey("content_type", "object_id")

    image = models.ImageField(upload_to=images_upload_to)
    image_type = models.CharField(
        max_length=50, choices=ImageType.choices, default=ImageType.DERMOSCOPIC
    )

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"Image {self.id} ({self.image_type}) for {self.content_type}:{self.object_id}"
