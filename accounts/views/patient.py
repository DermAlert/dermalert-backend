from rest_framework import viewsets, permissions, filters
from accounts.serializers.patient import PatientSerializer
from accounts.models import Patient


class PatientViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows patients to be viewed or edited.
    """

    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__name', 'user__cpf', 'sus_number']
    ordering_fields = ['user__name', 'date_of_birth', 'created_at']
    ordering = ['user__name']