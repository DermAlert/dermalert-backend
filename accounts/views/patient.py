from rest_framework import viewsets, permissions
from accounts.serializers.patient import PatientSerializer
from accounts.models import Patient
from django_filters import rest_framework as filters


class PatientViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows patients to be viewed or edited.
    """

    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = (filters.DjangoFilterBackend,)
