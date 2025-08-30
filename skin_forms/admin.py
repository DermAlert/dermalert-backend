from django.contrib import admin
from skin_forms.models import Wound


@admin.register(Wound)
class WoundAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"skin_condition_id",
		"height_mm",
		"width_mm",
		"total_score",
	)
