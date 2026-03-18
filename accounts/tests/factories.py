from datetime import date, timedelta

import factory
from django.contrib.auth import get_user_model
from accounts.models import Patient, Work
from accounts.enums.gender import Gender
from accounts.enums.permission_role import PermissionRole
from address.models import Address
from health_unit.models import HealthUnit

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
    other_gender = factory.LazyAttribute(
        lambda o: "Non-binary" if o.gender == Gender.OTHER else None
    )
    date_of_birth = factory.Faker("date_of_birth", minimum_age=0, maximum_age=120)


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address

    cep = factory.Sequence(lambda n: f"{10000000 + n}")
    country = "Brasil"
    state = factory.Faker("estado_sigla", locale="pt_BR")
    city = factory.Faker("city", locale="pt_BR")
    neighborhood = factory.Faker("bairro", locale="pt_BR")
    street = factory.Faker("street_name", locale="pt_BR")
    number = factory.Sequence(lambda n: n + 1)
    longitude = factory.Faker("longitude")
    latitude = factory.Faker("latitude")


class HealthUnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HealthUnit

    name = factory.Sequence(lambda n: f"Health Unit {n}")
    email = factory.Sequence(lambda n: f"unit{n}@example.com")
    address = factory.SubFactory(AddressFactory)


class WorkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Work

    user = factory.SubFactory(UserFactory)
    health_unit = factory.SubFactory(HealthUnitFactory)
    permission_role = PermissionRole.TECHNICIAN
    start_date = factory.LazyFunction(date.today)
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=30))
