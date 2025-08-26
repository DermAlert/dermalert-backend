from django.contrib import admin
from profile_forms.models import Phototype, ClinicalHistory, LifestyleRisk


@admin.register(Phototype)
class PhototypeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phototype", "score")
    list_filter = ("phototype",)


@admin.register(ClinicalHistory)
class ClinicalHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "hypertension",
        "diabetes",
        "deep_vein_thrombosis",
        "chronic_venous_insufficiency",
        "compression_stockings_use",
    )


@admin.register(LifestyleRisk)
class LifestyleRiskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "long_periods_posture",
        "leg_foot_trauma",
        "smoking",
        "physical_activity",
    )
