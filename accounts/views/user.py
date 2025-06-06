from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model
from accounts.serializers.user import UserSerializer
from accounts.filters.user import UserFilter

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("address").all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter
