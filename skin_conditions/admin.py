from django.contrib import admin
from skin_conditions.models import SkinCondition


@admin.register(SkinCondition)
class SkinConditionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "location", "created_at")
    list_filter = ("location",)
