from core.models import BaseModel
from django.db import models
from django.conf import settings


class ConsentTerm(BaseModel):
    """Termo de consentimento, versionado e com URL do documento."""

    version = models.PositiveIntegerField(unique=True)
    url = models.URLField(max_length=500)

    class Meta:
        ordering = ["-version"]

    def __str__(self) -> str:  # pragma: no cover
        return f"ConsentTerm v{self.version}"


class ConsentSignature(BaseModel):
    """Assinatura do usuário para um termo específico (N:N com payload)."""

    term = models.ForeignKey(
        ConsentTerm, on_delete=models.CASCADE, related_name="signatures"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consent_signatures",
    )
    has_signed = models.BooleanField(default=True)
    signed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["term", "user"], name="unique_user_term_signature"
            )
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"Signature user={self.user_id} term={self.term_id}"


def consent_signature_image_path(
    instance: "ConsentSignatureImage", filename: str
) -> str:
    # Folder by signature id to group pages
    return f"consent_signatures/{instance.signature_id}/{filename}"


class ConsentSignatureImage(BaseModel):
    """Imagens de páginas assinadas do termo físico."""

    signature = models.ForeignKey(
        ConsentSignature, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to=consent_signature_image_path)
    page_number = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["page_number", "id"]

    def __str__(self) -> str:  # pragma: no cover
        return f"SignatureImage {self.id} for signature {self.signature_id}"
