from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, permissions
from django_filters.rest_framework import DjangoFilterBackend

from skin_conditions.models import SkinCondition
from skin_conditions.serializers import (
    SkinConditionSerializer,
    SkinConditionDetailSerializer,
)


class SkinConditionNestedViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Nested under /patients/{user_pk}/skin-conditions

    - Allowed: list, retrieve, create
    - Not allowed: update (PUT/PATCH), delete
    """

    serializer_class = SkinConditionSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    queryset = SkinCondition.objects.all()
    pagination_class = None

    def get_queryset(self):
        user_id = self.kwargs.get("user_pk")
        return SkinCondition.objects.filter(user__id=user_id)

    def perform_create(self, serializer):
        user_id = self.kwargs["user_pk"]
        user = get_object_or_404(get_user_model(), id=user_id)
        serializer.save(user=user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SkinConditionDetailSerializer
        return super().get_serializer_class()
