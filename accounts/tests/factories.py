import factory
from django.contrib.auth import get_user_model
from accounts.models import Patient
from accounts.enums.gender import Gender

User = get_user_model()


def clear_str(cpf: str) -> str:
    """Remove non-numeric characters from CPF."""
    return "".join(filter(lambda x: x.isdigit(), cpf))


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("cpf",)
        exclude = ("raw_cpf",)

    raw_cpf = factory.Faker("cpf", locale="pt_BR")
    cpf = factory.LazyAttribute(lambda o: clear_str(o.raw_cpf))
    name = factory.Faker("name")
    email = factory.LazyAttribute(lambda o: f"{o.cpf}@ex.com")
    password = factory.PostGenerationMethodCall("set_password", "s3nh4!")


class PatientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Patient
        django_get_or_create = ("user",)
        exclude = (
            "raw_phone_number",
            "raw_sus_number",
        )

    raw_phone_number = factory.Faker("phone_number", locale="pt_BR")
    raw_sus_number = factory.Faker("random_int", min=10000000000, max=99999999999)

    user = factory.SubFactory(UserFactory)
    sus_number = factory.LazyAttribute(lambda o: str(o.raw_sus_number))
    phone_number = factory.LazyAttribute(lambda o: clear_str(o.raw_phone_number))
    gender = factory.Faker(
        "random_element", elements=[value for value, _ in Gender.choices]
    )
    date_of_birth = factory.Faker("date_of_birth", minimum_age=0, maximum_age=120)
