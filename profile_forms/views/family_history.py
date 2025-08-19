# views/family_history.py
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, permissions, generics, filters
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from profile_forms.models import (
    FamilyHistory,
    Parents,
    CancerTypes,
    InjuriesTreatment,
)
from profile_forms.serializers.family_history import (
    FamilyHistorySerializer,
    ParentsSerializer,
    CancerTypeSerializer,
    InjuriesTreatmentSerializer,
)


class FamilyHistorySingletonViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    POST /patients/{user_pk}/profile-forms/family-history/   -> cria
    GET  /patients/{user_pk}/profile-forms/family-history/   -> detalhe (singleton)
    """
    serializer_class = FamilyHistorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]

    def _get_object(self):
        user_id = self.kwargs["user_pk"]
        return get_object_or_404(FamilyHistory, user__id=user_id)

    def list(self, request, *args, **kwargs):
        obj = self._get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Evita duplicidade antes de validar nested, tal como no GeneralHealth
        user_id = self.kwargs.get("user_pk")
        user = get_object_or_404(get_user_model(), id=user_id)
        if FamilyHistory.objects.filter(user=user).exists():
            raise PermissionDenied("Já existe um formulário para esse CPF.")
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        user_id = self.kwargs["user_pk"]
        user = get_object_or_404(get_user_model(), id=user_id)
        serializer.save(user=user)



class ParentsListView(generics.ListAPIView):
    queryset = Parents.objects.all()
    serializer_class = ParentsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    pagination_class = None


class CancerTypeListView(generics.ListAPIView):
    queryset = CancerTypes.objects.all()
    serializer_class = CancerTypeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    pagination_class = None


class InjuriesTreatmentListView(generics.ListAPIView):
    queryset = InjuriesTreatment.objects.all()
    serializer_class = InjuriesTreatmentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    pagination_class = None
