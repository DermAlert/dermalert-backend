from django.contrib import admin
from .models import ConsentTerm, ConsentSignature, ConsentSignatureImage


@admin.register(ConsentTerm)
class ConsentTermAdmin(admin.ModelAdmin):
	list_display = ("id", "version", "url", "created_at")
	ordering = ("-version",)


class ConsentSignatureImageInline(admin.TabularInline):
	model = ConsentSignatureImage
	extra = 0


@admin.register(ConsentSignature)
class ConsentSignatureAdmin(admin.ModelAdmin):
	list_display = ("id", "term", "user", "has_signed", "signed_at")
	list_filter = ("has_signed", "term")
	inlines = [ConsentSignatureImageInline]
