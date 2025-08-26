from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, permissions, generics, filters
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from profile_forms.models import GeneralHealth, Allergy, Medicine, ChronicDisease
from profile_forms.serializers import (
    GeneralHealthSerializer,
    AllergySerializer,
    MedicineSerializer,
    ChronicDiseaseSerializer,
)


class GeneralHealthSingletonViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    POST /patients/{user_pk}/profile-forms/general-health/   -> cria
    GET  /patients/{user_pk}/profile-forms/general-health/   -> detalhe (singleton)
    """

    serializer_class = GeneralHealthSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]

    def _get_object(self):
        id = self.kwargs["user_pk"]
        return get_object_or_404(GeneralHealth, user__id=id)

    def list(self, request, *args, **kwargs):
        obj = self._get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Valida usuário e duplicidade antes de serializer.is_valid para evitar erros de unique nos nested
        user_id = self.kwargs.get("user_pk")
        user = get_object_or_404(get_user_model(), id=user_id)
        if GeneralHealth.objects.filter(user=user).exists():
            raise PermissionDenied("Já existe um formulário para esse CPF.")

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        id = self.kwargs["user_pk"]
        user = get_object_or_404(get_user_model(), id=id)
        serializer.save(user=user)


class AllergyListView(generics.ListAPIView):
    queryset = Allergy.objects.all()
    serializer_class = AllergySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    pagination_class = None


class MedicineListView(generics.ListAPIView):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    pagination_class = None


class ChronicDiseaseListView(generics.ListAPIView):
    queryset = ChronicDisease.objects.all()
    serializer_class = ChronicDiseaseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    pagination_class = None
