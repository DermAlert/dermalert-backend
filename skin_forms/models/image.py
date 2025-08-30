from core.models import BaseModel, models

from .wound import Wound


class WoundImage(BaseModel):
    wound = models.ForeignKey(Wound, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="wound_images/")

    def __str__(self) -> str:
        return f"WoundImage {self.id} for wound {self.wound_id}"
