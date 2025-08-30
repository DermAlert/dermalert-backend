from django.contrib import admin

from skin_forms.models import Wound
from skin_forms.models.image import Image


@admin.register(Wound)
class WoundAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"height_mm",
		"width_mm",
		"total_score",
		"created_at",
	)
	search_fields = ("id",)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
	list_display = ("id", "content_type", "object_id", "image_type", "created_at")
	search_fields = ("id",)
