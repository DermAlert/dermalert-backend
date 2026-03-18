from django_filters.rest_framework import FilterSet, CharFilter
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFilter(FilterSet):
    address = CharFilter(field_name="address_id")
    cpf = CharFilter(field_name="cpf", lookup_expr="icontains")
    name = CharFilter(field_name="name", lookup_expr="icontains")
    email = CharFilter(field_name="email", lookup_expr="icontains")

    class Meta:
        model = User
        fields = ["address", "cpf", "name", "email"]
