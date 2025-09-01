import factory

from accounts.tests.factories import UserFactory
from skin_conditions.enums import BodySite, SkinConditionType
from skin_conditions.models import SkinCondition


class SkinConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SkinCondition

    user = factory.SubFactory(UserFactory)
    location = factory.Faker(
        "random_element", elements=[value for value, _ in BodySite.choices]
    )
    type = factory.Faker(
        "random_element", elements=[value for value, _ in SkinConditionType.choices]
    )
