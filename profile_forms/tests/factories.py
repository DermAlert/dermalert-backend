import factory
from accounts.tests.factories import UserFactory
from profile_forms.models import GeneralHealth, ChronicDisease, Medicine, Allergy
from profile_forms.enums.general_health import PhysicalActivityFrequency
from profile_forms.models import (
    Relatives,
    CancerTypes,
    InjuriesTreatment,
    Phototype,
    RiskProtectiveFactors,
    CancerResearch,
    ClinicalHistory,
    LifestyleRisk,
    FamilyVascularHistory,
)
from profile_forms.enums.phototype import (
    SkinColor,
    EyesColor,
    HairColor,
    FrecklesAmount,
    SunExposureReaction,
    TannedSkinAbility,
    SunSensitivityFace,
)
from profile_forms.enums.risk_protective_factors import (
    SunExposurePeriod,
    SunBurnHistory,
    UVProtectionSPF,
    CheckupsFrequency,
)
from profile_forms.enums.cancer_research import HowLong
from profile_forms.enums.clinical_history import YesNoUnknown, CompressionStockingsUse
from profile_forms.enums.lifestyle_risk import (
    LongPeriodsPosture,
    YesNo,
    SmokingStatus,
)
from profile_forms.enums.clinical_history import YesNoUnknown as FvhYesNoUnknown


def clear_str(value: str) -> str:
    """Remove non-numeric characters from string."""
    return "".join(filter(lambda x: x.isdigit(), value))


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
        "random_element",
        elements=[value for value, _ in PhysicalActivityFrequency.choices],
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


class RiskProtectiveFactorsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RiskProtectiveFactors
        django_get_or_create = ("user",)

    user = factory.SubFactory(UserFactory)

    sun_exposure_period = factory.Faker(
        "random_element", elements=[value for value, _ in SunExposurePeriod.choices]
    )
    sun_burn = factory.Faker(
        "random_element", elements=[value for value, _ in SunBurnHistory.choices]
    )
    uv_protection = factory.Faker(
        "random_element", elements=[value for value, _ in UVProtectionSPF.choices]
    )
    hat_use = factory.Faker("pybool")
    artifitial_tan = factory.Faker("pybool")
    checkups_frequency = factory.Faker(
        "random_element", elements=[value for value, _ in CheckupsFrequency.choices]
    )
    cancer_campaigns = factory.Faker("pybool")


class CancerResearchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CancerResearch
        django_get_or_create = ("user",)

    user = factory.SubFactory(UserFactory)

    suspicious_moles = factory.Faker("pybool")
    bleed_itch = factory.Faker("pybool")
    how_long = factory.Faker(
        "random_element", elements=[value for value, _ in HowLong.choices]
    )
    lesion_aspect = factory.Faker("pybool")
    doctor_assistance = factory.Faker("pybool")
    diagnosis = factory.Faker("sentence")


class ClinicalHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClinicalHistory
        django_get_or_create = ("user",)

    user = factory.SubFactory(UserFactory)

    hypertension = factory.Faker(
        "random_element", elements=[value for value, _ in YesNoUnknown.choices]
    )
    diabetes = factory.Faker(
        "random_element", elements=[value for value, _ in YesNoUnknown.choices]
    )
    deep_vein_thrombosis = factory.Faker(
        "random_element", elements=[value for value, _ in YesNoUnknown.choices]
    )
    chronic_venous_insufficiency = factory.Faker(
        "random_element", elements=[value for value, _ in YesNoUnknown.choices]
    )
    compression_stockings_use = factory.Faker(
        "random_element",
        elements=[value for value, _ in CompressionStockingsUse.choices],
    )


class LifestyleRiskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LifestyleRisk
        django_get_or_create = ("user",)

    user = factory.SubFactory(UserFactory)
    long_periods_posture = factory.Faker(
        "random_element", elements=[value for value, _ in LongPeriodsPosture.choices]
    )
    leg_foot_trauma = factory.Faker(
        "random_element", elements=[value for value, _ in YesNo.choices]
    )
    smoking = factory.Faker(
        "random_element", elements=[value for value, _ in SmokingStatus.choices]
    )
    physical_activity = factory.Faker(
        "random_element", elements=[value for value, _ in YesNo.choices]
    )


class FamilyVascularHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FamilyVascularHistory
        django_get_or_create = ("user",)

    user = factory.SubFactory(UserFactory)
    family_leg_ulcers = factory.Faker(
        "random_element", elements=[value for value, _ in FvhYesNoUnknown.choices]
    )
    family_varicose_or_circulatory = factory.Faker(
        "random_element", elements=[value for value, _ in FvhYesNoUnknown.choices]
    )
