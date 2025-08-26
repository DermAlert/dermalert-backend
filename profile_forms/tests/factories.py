import factory
from accounts.tests.factories import UserFactory
from profile_forms.models import GeneralHealth, ChronicDisease, Medicine, Allergy
from profile_forms.enums.general_health import PhysicalActivityFrequency
from profile_forms.models import Relatives, CancerTypes, InjuriesTreatment, Phototype
from profile_forms.enums.phototype import (
    SkinColor,
    EyesColor,
    HairColor,
    FrecklesAmount,
    SunExposureReaction,
    TannedSkinAbility,
    SunSensitivityFace,
)

def clear_str(value: str) -> str:
    """Remove non-numeric characters from string."""
    return ''.join(filter(lambda x: x.isdigit(), value))

class ChronicDiseaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChronicDisease
        django_get_or_create = ("name",)

    name = factory.Faker("word")

class MedicineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Medicine
        django_get_or_create = ("name",)

    name = factory.Faker("word")

class AllergyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Allergy
        django_get_or_create = ("name",)

    name = factory.Faker("word")

class GeneralHealthFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GeneralHealth
        django_get_or_create = ("user",)

    user = factory.SubFactory(UserFactory)
    surgeries = factory.Faker("text", max_nb_chars=200)
    physical_activity_frequency = factory.Faker(
        "random_element", elements=[value for value, _ in PhysicalActivityFrequency.choices]
    )

    @factory.post_generation
    def chronic_diseases(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for chronic_disease in extracted:
                self.chronic_diseases.add(chronic_disease)

    @factory.post_generation
    def medicines(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for medicine in extracted:
                self.medicines.add(medicine)

    @factory.post_generation
    def allergies(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for allergy in extracted:
                self.allergies.add(allergy)

class RelativesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Relatives
        django_get_or_create = ("name",)

    name = factory.Faker("word")

class CancerTypesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CancerTypes
        django_get_or_create = ("name",)

    name = factory.Faker("word")

class InjuriesTreatmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InjuriesTreatment
        django_get_or_create = ("name",)

    name = factory.Faker("word")


class PhototypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Phototype
        django_get_or_create = ("user",)

    user = factory.SubFactory(UserFactory)

    skin_color = factory.Faker(
        "random_element", elements=[value for value, _ in SkinColor.choices]
    )
    eyes_color = factory.Faker(
        "random_element", elements=[value for value, _ in EyesColor.choices]
    )
    hair_color = factory.Faker(
        "random_element", elements=[value for value, _ in HairColor.choices]
    )
    freckles = factory.Faker(
        "random_element", elements=[value for value, _ in FrecklesAmount.choices]
    )
    sun_exposed = factory.Faker(
        "random_element", elements=[value for value, _ in SunExposureReaction.choices]
    )
    tanned_skin = factory.Faker(
        "random_element", elements=[value for value, _ in TannedSkinAbility.choices]
    )
    sun_sensitive_skin = factory.Faker(
        "random_element", elements=[value for value, _ in SunSensitivityFace.choices]
    )
