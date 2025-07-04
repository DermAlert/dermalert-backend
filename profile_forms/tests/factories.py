import factory
from django.contrib.auth import get_user_model
from profile_forms.models import GeneralHealth, ChronicDisease, Medicine, Allergy
from profile_forms.enums.general_health import PhysicalActivityFrequency

User = get_user_model()

def clear_str(value: str) -> str:
    """Remove non-numeric characters from string."""
    return ''.join(filter(lambda x: x.isdigit(), value))

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("cpf",)
        exclude = ("raw_cpf",)

    raw_cpf = factory.Faker('cpf', locale='pt_BR')
    cpf = factory.LazyAttribute(lambda o: clear_str(o.raw_cpf))
    name = factory.Faker("name")
    email = factory.LazyAttribute(lambda o: f"{o.cpf}@ex.com")
    password = factory.PostGenerationMethodCall("set_password", "s3nh4!")

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
