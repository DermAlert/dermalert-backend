from django.db.models import Q
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import (
    ManagerOrAdminPermission,
    ProfessionalManagementPermission,
    get_user_managed_health_unit_ids,
)
from accounts.serializers.patient import PatientSerializer
from accounts.serializers.work import ProfessionalAssignmentSerializer
from accounts.models import Patient, Work
from accounts.enums.permission_role import PermissionRole
from health_unit.models import HealthUnit
from health_unit.serializer import HealthUnitSerializer


class HealthUnitViewSet(viewsets.ModelViewSet):
    queryset = (
        HealthUnit.objects.select_related("address")
        .filter(is_deleted=False)
        .order_by("name")
    )
    serializer_class = HealthUnitSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "email", "address__city"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_permissions(self):
        if self.action in {"list", "retrieve", "create", "update", "partial_update", "destroy"}:
            return [permissions.IsAuthenticated(), ManagerOrAdminPermission()]
        if self.action in {"patients", "professionals"}:
            return [permissions.IsAuthenticated(), ProfessionalManagementPermission()]
        return [permissions.AllowAny()]

    @action(detail=True, methods=["get"])
    def professionals(self, request, pk=None):
        health_unit = self.get_object()
        managed_ids = get_user_managed_health_unit_ids(request.user)
        if managed_ids is not None and health_unit.pk not in managed_ids:
            return Response(
                {"detail": "You cannot view professionals for this health unit."},
                status=403,
            )

        queryset = Work.objects.select_related("user", "health_unit").filter(
            health_unit=health_unit,
            is_deleted=False,
            permission_role=PermissionRole.TECHNICIAN,
        )
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(user__name__icontains=search) | Q(user__cpf__icontains=search)
            )

        page = self.paginate_queryset(queryset.order_by("user__name"))
        if page is not None:
            serializer = ProfessionalAssignmentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProfessionalAssignmentSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def patients(self, request, pk=None):
        health_unit = self.get_object()
        managed_ids = get_user_managed_health_unit_ids(request.user)
        if managed_ids is not None and health_unit.pk not in managed_ids:
            return Response(
                {"detail": "You cannot view patients for this health unit."},
                status=403,
            )

        queryset = Patient.objects.select_related("user", "health_unit").filter(
            health_unit=health_unit,
            is_deleted=False,
        )
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(user__name__icontains=search)
                | Q(user__cpf__icontains=search)
                | Q(sus_number__icontains=search)
            )

        page = self.paginate_queryset(queryset.order_by("user__name"))
        if page is not None:
            serializer = PatientSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PatientSerializer(queryset, many=True)
        return Response(serializer.data)
