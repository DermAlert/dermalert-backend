from django.db import models
from django.conf import settings
from .base_form import BaseForm
from profile_forms.enums.phototype import (
    SkinColor,
    EyesColor,
    HairColor,
    FrecklesAmount,
    SunExposureReaction,
    TannedSkinAbility,
    SunSensitivityFace,
    PhototypeClass,
)


# Scoring tables based on the UI steps (1..7). Values chosen to map to a typical Fitzpatrick-like scale.
SKIN_COLOR_POINTS = {
    SkinColor.MILKY_WHITE: 0,
    SkinColor.WHITE: 2,
    SkinColor.WHITE_TO_BEIGE_GOLDEN: 4,
    SkinColor.BEIGE: 8,
    SkinColor.LIGHT_BROWN: 12,
    SkinColor.DARK_BROWN: 16,
    SkinColor.BLACK: 20,
}

EYES_COLOR_POINTS = {
    EyesColor.LIGHT_BLUE_GRAY_GREEN: 0,
    EyesColor.BLUE_GRAY_GREEN: 1,
    EyesColor.BLUE: 2,
    EyesColor.LIGHT_BROWN: 3,
    EyesColor.DARK_BROWN: 4,
}

HAIR_COLOR_POINTS = {
    HairColor.RED_LIGHT_BLOND: 0,
    HairColor.BLOND_LIGHT_BROWN: 1,
    HairColor.BROWN: 2,
    HairColor.DARK_BROWN: 3,
    HairColor.BLACK: 4,
}

FRECKLES_POINTS = {
    FrecklesAmount.MANY: 0,
    FrecklesAmount.SOME: 1,
    FrecklesAmount.FEW: 2,
    FrecklesAmount.NONE: 3,
}

SUN_EXPOSED_POINTS = {
    SunExposureReaction.ALWAYS_BURNS_PEELS_PAINFUL: 0,
    SunExposureReaction.BURNS_PEELS_A_LITTLE: 2,
    SunExposureReaction.BURNS_NO_PEEL: 4,
    SunExposureReaction.SELDOM_OR_NOT_RED: 6,
    SunExposureReaction.NEVER_RED: 8,
}

TANNED_SKIN_POINTS = {
    TannedSkinAbility.NEVER_ALWAYS_BURNS: 0,
    TannedSkinAbility.SOMETIMES: 2,
    TannedSkinAbility.OFTEN: 4,
    TannedSkinAbility.ALWAYS: 6,
}

SUN_SENSITIVE_POINTS = {
    SunSensitivityFace.VERY_SENSITIVE: 0,
    SunSensitivityFace.SENSITIVE: 1,
    SunSensitivityFace.NORMAL: 2,
    SunSensitivityFace.RESISTANT: 3,
    SunSensitivityFace.VERY_RESISTANT_NEVER_BURNS: 4,
}


def classify_phototype(score: int) -> PhototypeClass:
    """Classify phototype from total score using provided thresholds:
    0–7: I, 8–16: II, 17–25: III, 26–30: IV, >30: V–VI.
    As the last bucket merges V and VI, we split it pragmatically: 31–40 -> V, >40 -> VI.
    """
    if 0 <= score <= 7:
        return PhototypeClass.I
    if 8 <= score <= 16:
        return PhototypeClass.II
    if 17 <= score <= 25:
        return PhototypeClass.III
    if 26 <= score <= 30:
        return PhototypeClass.IV
    if 31 <= score <= 40:
        return PhototypeClass.V
    return PhototypeClass.VI


class Phototype(BaseForm):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="phototype",
    )

    skin_color = models.CharField(max_length=50, choices=SkinColor.choices)
    eyes_color = models.CharField(max_length=50, choices=EyesColor.choices)
    hair_color = models.CharField(max_length=50, choices=HairColor.choices)
    freckles = models.CharField(max_length=50, choices=FrecklesAmount.choices)
    sun_exposed = models.CharField(max_length=80, choices=SunExposureReaction.choices)
    tanned_skin = models.CharField(max_length=50, choices=TannedSkinAbility.choices)
    sun_sensitive_skin = models.CharField(max_length=80, choices=SunSensitivityFace.choices)

    # Auto-calculated
    phototype = models.CharField(
        max_length=5,
        choices=PhototypeClass.choices,
        blank=True,
        null=True,
    )
    score = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Phototype"
        verbose_name_plural = "Phototypes"

    def calculate_score(self) -> int:
        return (
            SKIN_COLOR_POINTS.get(self.skin_color, 0)
            + EYES_COLOR_POINTS.get(self.eyes_color, 0)
            + HAIR_COLOR_POINTS.get(self.hair_color, 0)
            + FRECKLES_POINTS.get(self.freckles, 0)
            + SUN_EXPOSED_POINTS.get(self.sun_exposed, 0)
            + TANNED_SKIN_POINTS.get(self.tanned_skin, 0)
            + SUN_SENSITIVE_POINTS.get(self.sun_sensitive_skin, 0)
        )

    def save(self, *args, **kwargs):
        total = self.calculate_score()
        self.score = total
        self.phototype = classify_phototype(total)
        super().save(*args, **kwargs)
