import io

import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from accounts.tests.factories import UserFactory
from skin_conditions.enums import BodySite
from skin_conditions.models import SkinCondition
from skin_forms.enums.wound import (
    DepthOfTissueInjury,
    ExudateType,
    WoundBedTissue,
    WoundEdges,
)
from skin_forms.models import Wound, WoundImage, Cancer, CancerImage
from skin_forms.enums.cancer import Asymmetry, Border, ColorVariation, Diameter, Evolution


def _make_image_file(name="test.png", size=(16, 16), color=(155, 0, 0)):
    file_obj = io.BytesIO()
    image = Image.new("RGB", size, color)
    image.save(file_obj, "PNG")
    file_obj.seek(0)
    return SimpleUploadedFile(name, file_obj.read(), content_type="image/png")


class SkinConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SkinCondition

    user = factory.SubFactory(UserFactory)
    location = factory.Faker(
        "random_element", elements=[value for value, _ in BodySite.choices]
    )
    description = factory.Faker("sentence")


class WoundFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Wound

    skin_condition = factory.SubFactory(SkinConditionFactory)
    height_mm = 10
    width_mm = 10
    wound_edges = WoundEdges.NO_EDGES
    wound_bed_tissue = WoundBedTissue.REGENERATED_SCARRED
    depth_of_tissue_injury = DepthOfTissueInjury.INTACT_SKIN
    exudate_type = ExudateType.DRY

    increased_pain = False
    perilesional_erythema = False
    perilesional_edema = False
    heat_or_warm_skin = False
    increased_exudate = False
    purulent_exudate = False
    friable_tissue = False
    stagnant_wound = False
    biofilm_compatible_tissue = False
    odor = False
    hypergranulation = False
    wound_size_increase = False
    satallite_lesions = False
    grayish_wound_bed = False


class WoundImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WoundImage

    wound = factory.SubFactory(WoundFactory)
    image = factory.LazyFunction(_make_image_file)


class CancerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cancer

    skin_condition = factory.SubFactory(SkinConditionFactory)
    asymmetry = Asymmetry.SYMMETRIC
    border = Border.REGULAR_WELL_DEFINED
    color_variation = ColorVariation.SINGLE_COLOR
    diameter = Diameter.UNDER_6MM
    evolution = Evolution.NO_CHANGES


class CancerImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CancerImage

    cancer = factory.SubFactory(CancerFactory)
    image = factory.LazyFunction(_make_image_file)
