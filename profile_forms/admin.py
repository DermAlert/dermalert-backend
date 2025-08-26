from django.contrib import admin
from profile_forms.models import Phototype


@admin.register(Phototype)
class PhototypeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phototype", "score")
    list_filter = ("phototype",)
