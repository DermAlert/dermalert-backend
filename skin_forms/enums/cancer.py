from django.db import models
from django.utils.translation import gettext_lazy as _


class Asymmetry(models.TextChoices):
    SYMMETRIC = "symmetric", _("Sim, a lesão é simétrica (forma uniforme)")
    ASYMMETRIC = (
        "asymmetric",
        _("Não, a lesão é assimétrica (uma metade é diferente da outra)"),
    )


class Border(models.TextChoices):
    REGULAR_WELL_DEFINED = "regular_well_defined", _("Regulares e bem definidas")
    IRREGULAR_POORLY_DEFINED = (
        "irregular_poorly_defined",
        _("Irregulares, mal definidas, com contornos serrilhados ou borrados"),
    )


class ColorVariation(models.TextChoices):
    SINGLE_COLOR = "single_color", _("Uma única cor (ex: castanho claro ou escuro)")
    THREE_OR_MORE_COLORS = (
        "three_or_more_colors",
        _("Três ou mais cores (ex: marrom, preto, vermelho, branco, azul)"),
    )


class Diameter(models.TextChoices):
    UNDER_6MM = "under_6mm", _("Menor que 6 mm (menor que uma borracha de lápis)")
    OVER_OR_EQUAL_6MM = "over_or_equal_6mm", _("Maior ou igual a 6 mm.")


class Evolution(models.TextChoices):
    NO_CHANGES = "no_changes", _("Não houve mudanças perceptíveis nos últimos meses")
    RECENT_CHANGES = (
        "recent_changes",
        _("Houve mudança de forma, tamanho, cor, coceira ou sangramento recentemente"),
    )
