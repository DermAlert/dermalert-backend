from rest_framework import viewsets, permissions, filters
from accounts.serializers.patient import PatientSerializer
from accounts.models import Patient


class PatientViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows patients to be viewed or edited.
    
    Search:
    Search by patient name, CPF, or SUS number.
    - Example: GET /api/patients/?search=João
    - Example: GET /api/patients/?search=12345678901
    
    Ordering:
    Order by patient name, date of birth, or creation date.
    - Example: GET /api/patients/?ordering=user__name
    - Example: GET /api/patients/?ordering=-date_of_birth
    - Example: GET /api/patients/?ordering=created_at
    
    Combined Search and Ordering:
    - Example: GET /api/patients/?search=Silva&ordering=-date_of_birth
    """

    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__name', 'user__cpf', 'sus_number']
    ordering_fields = ['user__name', 'date_of_birth', 'created_at']
    ordering = ['user__name']