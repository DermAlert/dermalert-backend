from django.contrib import admin
from skin_forms.models import Wound, WoundImage, Cancer, CancerImage


@admin.register(Wound)
class WoundAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"skin_condition_id",
		"height_mm",
		"width_mm",
		"total_score",
	)


@admin.register(WoundImage)
class WoundImageAdmin(admin.ModelAdmin):
	list_display = ("id", "wound_id", "image")


@admin.register(Cancer)
class CancerAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"asymmetry",
		"border",
		"color_variation",
		"diameter",
		"evolution",
	)


@admin.register(CancerImage)
class CancerImageAdmin(admin.ModelAdmin):
	list_display = ("id", "cancer_id", "image")
