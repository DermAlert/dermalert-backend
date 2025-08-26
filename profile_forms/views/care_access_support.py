from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

from profile_forms.models import CareAccessSupport
from profile_forms.serializers.care_access_support import CareAccessSupportSerializer


class CareAccessSupportSingletonViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CareAccessSupportSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]

    def _get_object(self):
        user_id = self.kwargs["user_pk"]
        return get_object_or_404(CareAccessSupport, user__id=user_id)

    def list(self, request, *args, **kwargs):
        obj = self._get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user_id = self.kwargs.get("user_pk")
        user = get_object_or_404(get_user_model(), id=user_id)
        if CareAccessSupport.objects.filter(user=user).exists():
            raise PermissionDenied("A form already exists for this patient.")
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        user_id = self.kwargs["user_pk"]
        user = get_object_or_404(get_user_model(), id=user_id)
        serializer.save(user=user)
