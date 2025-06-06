from django_filters.rest_framework import FilterSet, NumberFilter
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFilter(FilterSet):
    address = NumberFilter(field_name="address_id")

    class Meta:
        model = User
        fields = ["address"]
