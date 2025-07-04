from django_filters.rest_framework import FilterSet, NumberFilter, CharFilter
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFilter(FilterSet):
    address = NumberFilter(field_name="address_id")
    cpf = NumberFilter(field_name="cpf")
    name = CharFilter(field_name="name")

    class Meta:
        model = User
        fields = ["address", "cpf", "name"]
