from django.db import models


class SkinColor(models.TextChoices):
    MILKY_WHITE = "milky_white", "Milky white"
    WHITE = "white", "White"
    WHITE_TO_BEIGE_GOLDEN = "white_to_beige_golden", "White to beige, golden undertone"
    BEIGE = "beige", "Beige"
    LIGHT_BROWN = "light_brown", "Light brown"
    DARK_BROWN = "dark_brown", "Dark brown"
    BLACK = "black", "Black"


class EyesColor(models.TextChoices):
    LIGHT_BLUE_GRAY_GREEN = "light_blue_gray_green", "Light blue, gray, green"
    BLUE_GRAY_GREEN = "blue_gray_green", "Blue, gray or green"
    BLUE = "blue", "Blue"
    LIGHT_BROWN = "light_brown", "Light brown"
    DARK_BROWN = "dark_brown", "Dark brown"


class HairColor(models.TextChoices):
    RED_LIGHT_BLOND = "red_light_blond", "Red, light blond"
    BLOND_LIGHT_BROWN = "blond_light_brown", "Blond, light brown"
    BROWN = "brown", "Brown"
    DARK_BROWN = "dark_brown", "Dark brown"
    BLACK = "black", "Black"


class FrecklesAmount(models.TextChoices):
    MANY = "many", "Many"
    SOME = "some", "Some"
    FEW = "few", "Few"
    NONE = "none", "None"


class SunExposureReaction(models.TextChoices):
    ALWAYS_BURNS_PEELS_PAINFUL = (
        "always_burns_peels_painful",
        "Always burns, painful, peels",
    )
    BURNS_PEELS_A_LITTLE = "burns_peels_a_little", "Burns, peels a little"
    BURNS_NO_PEEL = "burns_no_peel", "Burns, doesn’t peel"
    SELDOM_OR_NOT_RED = "seldom_or_not_red", "Seldom red or not at all"
    NEVER_RED = "never_red", "Never red"


class TannedSkinAbility(models.TextChoices):
    NEVER_ALWAYS_BURNS = "never_always_burns", "Never, always burns"
    SOMETIMES = "sometimes", "Sometimes"
    OFTEN = "often", "Often"
    ALWAYS = "always", "Always"


class SunSensitivityFace(models.TextChoices):
    VERY_SENSITIVE = "very_sensitive", "Very sensitive"
    SENSITIVE = "sensitive", "Sensitive"
    NORMAL = "normal", "Normal"
    RESISTANT = "resistant", "Resistant"
    VERY_RESISTANT_NEVER_BURNS = (
        "very_resistant_never_burns",
        "Very resistant, never burns",
    )


class PhototypeClass(models.TextChoices):
    I = "I", "Phototype I"
    II = "II", "Phototype II"
    III = "III", "Phototype III"
    IV = "IV", "Phototype IV"
    V = "V", "Phototype V"
    VI = "VI", "Phototype VI"
