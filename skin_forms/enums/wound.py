from django.db import models
from django.utils.translation import gettext_lazy as _


#
# ITEM 01 - Dimensão da lesão
#
class LesionDimension:
    """
    Dimensão da lesão (altura x largura) em cm².
    Retorna a pontuação de acordo com a área calculada:

    - Área = 0cm² => 0 pontos
    - Área < 4cm² => 1 ponto
    - Área entre 4 e 16cm² => 2 pontos
    - Área entre 16 e 36cm² => 3 pontos
    - Área entre 36 e 64cm² => 4 pontos
    - Área entre 64 e 100cm² => 5 pontos
    - Área > 100cm² => 6 pontos
    """

    @staticmethod
    def get_points(height_cm: float, width_cm: float) -> int:
        area = height_cm * width_cm
        if area == 0:
            return 0
        elif area < 4:
            return 1
        elif area < 16:
            return 2
        elif area < 36:
            return 3
        elif area < 64:
            return 4
        elif area < 100:
            return 5
        else:
            return 6


#
# ITEM 02 - Profundidade dos tecidos afetados
#
class DepthOfTissueInjury(models.TextChoices):
    INTACT_SKIN = "intact_skin", _("Pele intacta ou cicatrizada")
    EPIDERMIS_DERMIS = "epidermis_dermis", _("Atingimento de epiderme e derme")
    HYPODERMIS_SUBCUTANEOUS = (
        "hypodermis_subcutaneous",
        _(
            "Atingimento de hipoderme ou tela subcutânea "
            "(tecido adiposo sem atingir fáscia muscular)"
        ),
    )
    MUSCLE_TISSUE = "muscle_tissue", _("Atingimento de tecido muscular")
    BONE_TISSUE = (
        "bone_tissue",
        _(
            "Atingimento de tecido ósseo e/ou tecidos anexos "
            "(tendões, ligamentos, cápsula articular) ou necrose negra"
        ),
    )

    @classmethod
    def get_points(cls, choice):
        mapping = {
            cls.INTACT_SKIN: 0,
            cls.EPIDERMIS_DERMIS: 1,
            cls.HYPODERMIS_SUBCUTANEOUS: 2,
            cls.MUSCLE_TISSUE: 3,
            cls.BONE_TISSUE: 4,
        }
        return mapping.get(choice, 0)


#
# ITEM 03 - Bordos
#
class WoundEdges(models.TextChoices):
    NO_EDGES = "no_edges", _("Ausência de bordos da ferida")
    DIFFUSE = "diffuse", _("Difusos")
    WELL_DEFINED = "well_defined", _("Delimitados")
    DAMAGED = "damaged", _("Danificados")
    THICKENED = "thickened", _("Espessados (“envelhecidos”, “evertidos”)")

    @classmethod
    def get_points(cls, choice):
        mapping = {
            cls.NO_EDGES: 0,
            cls.DIFFUSE: 1,
            cls.WELL_DEFINED: 2,
            cls.DAMAGED: 3,
            cls.THICKENED: 4,
        }
        return mapping.get(choice, 0)


#
# ITEM 04 - Tipo de tecido no leito da ferida
#
class WoundBedTissue(models.TextChoices):
    REGENERATED_SCARRED = "regenerated_scarred", _("Tecido regenerado ou cicatrizado")
    EPITHELIALIZATION = "epithelialization", _("Tecido de epitelização")
    GRANULATION = "granulation", _("Tecido de granulação")
    DEVITALIZED_FIBRINOUS = (
        "devitalized_fibrinous",
        _("Tecido desvitalizado e/ou fibrinoso"),
    )
    NECROTIC = "necrotic", _("Tecido necrosado (necrose seca ou úmida)")

    @classmethod
    def get_points(cls, choice):
        mapping = {
            cls.REGENERATED_SCARRED: 0,
            cls.EPITHELIALIZATION: 1,
            cls.GRANULATION: 2,
            cls.DEVITALIZED_FIBRINOUS: 3,
            cls.NECROTIC: 4,
        }
        return mapping.get(choice, 0)


#
# ITEM 05 - Exsudato
#
class ExudateType(models.TextChoices):
    DRY = "dry", _("Seco")
    MOIST = "moist", _("Úmido")
    WET = "wet", _("Molhado")
    SATURATED = "saturated", _("Saturado")
    LEAKAGE = "leakage", _("Com fuga de exsudato")

    @classmethod
    def get_points(cls, choice):
        mapping = {
            cls.DRY: 3,
            cls.MOIST: 0,
            cls.WET: 1,
            cls.SATURATED: 2,
            cls.LEAKAGE: 3,
        }
        return mapping.get(choice, 0)


class WoundLocation(models.TextChoices):
    HEAD_NECK = "head_neck", _("Cabeça e Pescoço")
    UPPER_LIMBS = "upper_limbs", _("Membros Superiores")
    LOWER_LIMBS = "lower_limbs", _("Membros Inferiores")
    TORSO = "torso", _("Tronco")
    SACRAL_REGION = "sacral_region", _("Região Sacral")
    OTHER = "other", _("Outros")
