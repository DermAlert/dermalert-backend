import factory
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("cpf",)

    cpf = factory.Sequence(lambda n: f"{n:011}")
    name = factory.Faker("name")
    email = factory.LazyAttribute(lambda o: f"{o.cpf}@ex.com")
    password = factory.PostGenerationMethodCall("set_password", "s3nh4!")
