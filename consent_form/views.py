from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import ConsentTerm, ConsentSignature
from .serializers import (
    ConsentTermSerializer,
    ConsentSignatureSerializer,
    ConsentSignatureCreateSerializer,
    NeedsSignatureResponseSerializer,
    ConsentSignatureListItemSerializer,
)


class ConsentTermViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Apenas leitura via API: lista e endpoint para pegar a última versão."""

    queryset = ConsentTerm.objects.all()
    serializer_class = ConsentTermSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    @action(detail=False, methods=["get"], url_path="latest")
    def latest(self, request, *args, **kwargs):
        latest = self.queryset.order_by("-version").first()
        if not latest:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response(self.get_serializer(latest).data)


class PatientConsentViewSet(viewsets.GenericViewSet):
    """
    Rotas aninhadas em patients para verificar e enviar assinaturas:
      - GET   /patients/{user_pk}/consent/needs-signature/ -> bool + term versão
      - POST  /patients/{user_pk}/consent/sign/ -> assina um termo específico com imagens
    """

    serializer_class = NeedsSignatureResponseSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_user(self):
        return get_object_or_404(get_user_model(), id=self.kwargs.get("user_pk"))

    def get_serializer_class(self):
        if self.action == "sign":
            return ConsentSignatureCreateSerializer
        if self.action == "signed_terms":
            return ConsentSignatureListItemSerializer
        return NeedsSignatureResponseSerializer

    @action(detail=False, methods=["get"], url_path="needs-signature")
    def needs_signature(self, request, *args, **kwargs):
        user = self.get_user()
        latest = ConsentTerm.objects.order_by("-version").first()
        if not latest:
            data = {"needs_signature": False, "reason": "no_terms"}
            return Response(NeedsSignatureResponseSerializer(data).data)
        exists = ConsentSignature.objects.filter(
            user=user, term=latest, has_signed=True
        ).exists()
        data = {
            "needs_signature": not exists,
            "latest_term": ConsentTermSerializer(latest).data,
        }
        return Response(NeedsSignatureResponseSerializer(data).data)

    @action(detail=False, methods=["post"], url_path="sign")
    def sign(self, request, *args, **kwargs):
        user = self.get_user()
        serializer = ConsentSignatureCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        term = get_object_or_404(ConsentTerm, id=serializer.validated_data["term"].id)
        # Evita duplicidade: se já assinou este termo, retorna 400
        if ConsentSignature.objects.filter(user=user, term=term).exists():
            return Response(
                {"detail": "already signed"}, status=status.HTTP_400_BAD_REQUEST
            )
        signature = serializer.save(user=user)
        return Response(
            ConsentSignatureSerializer(signature).data, status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["get"], url_path="signed-terms")
    def signed_terms(self, request, *args, **kwargs):
        """Lista todos os termos já assinados pelo usuário (mais recente primeiro)."""
        user = self.get_user()
        qs = (
            ConsentSignature.objects.filter(user=user, has_signed=True)
            .select_related("term")
            .prefetch_related("images")
            .order_by("-signed_at", "-term__version")
        )
        serializer = ConsentSignatureListItemSerializer(qs, many=True)
        return Response(serializer.data)
