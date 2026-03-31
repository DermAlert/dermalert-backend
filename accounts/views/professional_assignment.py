from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import filters, permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from accounts.enums.permission_role import PermissionRole
from accounts.permissions import (
    ProfessionalManagementPermission,
    get_user_managed_health_unit_ids,
    user_can_manage_health_unit,
)
from accounts.serializers.work import (
    ProfessionalAssignmentSerializer,
    ProfessionalAssignmentUpdateSerializer,
    ProfessionalAssignmentWriteSerializer,
)
from accounts.services import assign_professional_to_health_unit, resolve_user_by_identity
from accounts.models import Work


class ProfessionalAssignmentViewSet(viewsets.ModelViewSet):
    queryset = (
        Work.objects.select_related("user", "health_unit")
        .filter(is_deleted=False)
        .order_by("user__name", "health_unit__name")
    )
    serializer_class = ProfessionalAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, ProfessionalManagementPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__name", "user__cpf"]
    ordering_fields = ["user__name", "start_date", "created_at"]
    ordering = ["user__name"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset.none()

        queryset = super().get_queryset()
        managed_ids = get_user_managed_health_unit_ids(self.request.user)
        if managed_ids is None:
            return queryset
        return queryset.filter(health_unit_id__in=managed_ids)

    def get_serializer_class(self):
        if self.action == "create":
            return ProfessionalAssignmentWriteSerializer
        if self.action in {"update", "partial_update"}:
            return ProfessionalAssignmentUpdateSerializer
        return ProfessionalAssignmentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        health_unit = serializer.validated_data["health_unit"]
        if not user_can_manage_health_unit(request.user, health_unit.pk):
            raise PermissionDenied("You cannot manage professionals for this health unit.")

        try:
            work, assignment_status = assign_professional_to_health_unit(
                created_by=request.user,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict) from exc
        response_serializer = ProfessionalAssignmentSerializer(
            work, context=self.get_serializer_context()
        )
        message = (
            "Registration invite sent successfully."
            if assignment_status == "invited"
            else "Professional linked successfully."
        )
        return Response(
            {
                "status": assignment_status,
                "message": message,
                "assignment": response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def _update_assignment(self, request, *args, partial=False, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance=instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)

        candidate_cpf = serializer.validated_data.get("cpf", instance.user.cpf)
        candidate_email = serializer.validated_data.get("email", instance.user.email)
        other_user = resolve_user_by_identity(
            cpf=candidate_cpf,
            email=candidate_email,
            exclude_user=instance.user,
        )
        if other_user is not None:
            raise ValidationError(
                {"detail": "CPF and email must continue to belong to the same professional."}
            )

        for field in ["name", "cpf", "email"]:
            if field in serializer.validated_data:
                setattr(instance.user, field, serializer.validated_data[field])
        instance.user.save()

        for field in ["permission_role", "start_date", "end_date"]:
            if field in serializer.validated_data:
                setattr(instance, field, serializer.validated_data[field])

        instance.updated_by = request.user
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict) from exc
        instance.save()

        return Response(
            ProfessionalAssignmentSerializer(
                instance, context=self.get_serializer_context()
            ).data
        )

    def update(self, request, *args, **kwargs):
        return self._update_assignment(request, *args, partial=False, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self._update_assignment(request, *args, partial=True, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.is_deleted = True
        instance.updated_by = request.user
        instance.save(update_fields=["is_active", "is_deleted", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfessionalViewSet(ProfessionalAssignmentViewSet):
    def get_queryset(self):
        return super().get_queryset().filter(permission_role=PermissionRole.TECHNICIAN)


class ManagerViewSet(ProfessionalAssignmentViewSet):
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return super().get_queryset().filter(permission_role=PermissionRole.MANAGER)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data={**request.data, "permission_role": PermissionRole.MANAGER}
        )
        serializer.is_valid(raise_exception=True)

        health_unit = serializer.validated_data["health_unit"]
        if not user_can_manage_health_unit(request.user, health_unit.pk):
            raise PermissionDenied("You cannot manage professionals for this health unit.")

        try:
            work, assignment_status = assign_professional_to_health_unit(
                created_by=request.user,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict) from exc

        response_serializer = ProfessionalAssignmentSerializer(
            work, context=self.get_serializer_context()
        )
        return Response(
            {
                "status": assignment_status,
                "message": "Manager created successfully."
                if assignment_status == "linked"
                else "Manager invite sent successfully.",
                "assignment": response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
