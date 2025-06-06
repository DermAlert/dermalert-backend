from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from address.models import Address
from address.serializer import (
    AddressSerializer,
    CepRequestSerializer,
    AddressResponseSerializer,
)
from address.services import fetch_address_from_cep


class AddressViewSet(ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [AllowAny]
    filter_backends = ()

    @action(detail=False, methods=["post"], url_path="cep-lookup")
    def cep_lookup(self, request):
        lookup = CepRequestSerializer(data=request.data)
        lookup.is_valid(raise_exception=True)

        cep = lookup.validated_data["cep"]

        try:
            data = fetch_address_from_cep(cep)
        except ValueError:
            return Response({"detail": "CEP não encontrado."}, status=404)
        except Exception:
            return Response({"detail": "Erro no serviço de CEP."}, status=502)

        out = AddressResponseSerializer(data=data)
        out.is_valid(raise_exception=True)
        return Response(out.data)
