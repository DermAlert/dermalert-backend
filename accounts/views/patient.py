from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from accounts.serializers.patient import PatientSerializer
from accounts.models import Patient
from accounts.permissions import (
    PatientViewPermission,
    get_user_health_unit_ids,
    user_can_access_health_unit,
    user_is_admin,
    user_is_manager,
)


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

    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, PatientViewPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__name", "user__cpf", "sus_number"]
    ordering_fields = ["user__name", "date_of_birth", "created_at"]
    ordering = ["user__name"]

    def get_queryset(self):
        queryset = (
            Patient.objects.select_related("user", "health_unit")
            .filter(is_deleted=False)
            .order_by("user__name")
        )
        if user_is_admin(self.request.user) or user_is_manager(self.request.user):
            return queryset

        unit_ids = get_user_health_unit_ids(self.request.user)
        return queryset.filter(health_unit_id__in=unit_ids)

    def perform_create(self, serializer):
        health_unit = serializer.validated_data.get("health_unit")
        if health_unit is None and not (
            user_is_admin(self.request.user) or user_is_manager(self.request.user)
        ):
            unit_ids = get_user_health_unit_ids(self.request.user)
            if len(unit_ids) != 1:
                raise PermissionDenied("Health unit is required for this patient.")
            serializer.save(health_unit_id=unit_ids[0])
            return

        if health_unit is not None and not user_can_access_health_unit(
            self.request.user, health_unit.pk
        ):
            raise PermissionDenied("You cannot link this patient to that health unit.")

        serializer.save()

    def perform_update(self, serializer):
        health_unit = serializer.validated_data.get("health_unit")
        if health_unit is not None and not user_can_access_health_unit(
            self.request.user, health_unit.pk
        ):
            raise PermissionDenied("You cannot move this patient to that health unit.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.is_deleted = True
        instance.health_unit = None
        instance.save(update_fields=["is_active", "is_deleted", "health_unit"])
        return Response(status=status.HTTP_204_NO_CONTENT)
