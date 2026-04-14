from accounts.enums.permission_role import PermissionRole
from accounts.models import Patient, Work
from rest_framework.permissions import BasePermission

ROLE_ADMIN = "admin"
ROLE_MANAGER = "manager"
ROLE_SUPERVISOR = "supervisor"
ROLE_PROFESSIONAL = "professional"


def user_is_admin(user) -> bool:
    return bool(
        user
        and user.is_authenticated
        and (user.is_staff or user.is_superuser)
    )


def user_is_manager(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    return Work.objects.filter(
        user=user,
        permission_role=PermissionRole.MANAGER,
        is_active=True,
        is_deleted=False,
    ).exists()


def user_is_supervisor(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    return Work.objects.filter(
        user=user,
        permission_role=PermissionRole.SUPERVISOR,
        is_active=True,
        is_deleted=False,
    ).exists()


def user_is_professional(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    return Work.objects.filter(
        user=user,
        permission_role=PermissionRole.TECHNICIAN,
        is_active=True,
        is_deleted=False,
    ).exists()


def get_user_roles(user):
    roles = set()
    if user_is_admin(user):
        roles.add(ROLE_ADMIN)
    if user_is_manager(user):
        roles.add(ROLE_MANAGER)
    if user_is_supervisor(user):
        roles.add(ROLE_SUPERVISOR)
    if user_is_professional(user):
        roles.add(ROLE_PROFESSIONAL)
    return roles


def get_user_health_unit_ids(user):
    if not user or not user.is_authenticated:
        return []

    return list(
        Work.objects.filter(
            user=user,
            is_active=True,
            is_deleted=False,
        ).values_list("health_unit_id", flat=True)
    )


def get_user_managed_health_unit_ids(user):
    if not user or not user.is_authenticated:
        return []

    if user_is_admin(user) or user_is_manager(user):
        return None

    return list(
        Work.objects.filter(
            user=user,
            permission_role=PermissionRole.SUPERVISOR,
            is_active=True,
            is_deleted=False,
        ).values_list("health_unit_id", flat=True)
    )


def user_can_manage_health_unit(user, health_unit_id) -> bool:
    managed_ids = get_user_managed_health_unit_ids(user)
    if managed_ids is None:
        return True
    return health_unit_id in managed_ids


def user_can_access_health_unit(user, health_unit_id) -> bool:
    if user_is_admin(user) or user_is_manager(user):
        return True

    return health_unit_id in get_user_health_unit_ids(user)


def user_can_access_patient(user, patient_user_id) -> bool:
    try:
        patient_user_id = int(patient_user_id)
    except (TypeError, ValueError):
        return False

    if user_is_admin(user) or user_is_manager(user):
        return True

    patient = (
        Patient.objects.filter(user_id=patient_user_id, is_deleted=False)
        .values("health_unit_id")
        .first()
    )
    if not patient or patient["health_unit_id"] is None:
        return False

    return patient["health_unit_id"] in get_user_health_unit_ids(user)


class ClinicalAccessPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and get_user_roles(request.user))


class ProfessionalManagementPermission(BasePermission):
    def has_permission(self, request, view):
        roles = get_user_roles(request.user)
        return bool(roles & {ROLE_ADMIN, ROLE_MANAGER, ROLE_SUPERVISOR})

    def has_object_permission(self, request, view, obj):
        roles = get_user_roles(request.user)
        return bool(roles & {ROLE_ADMIN, ROLE_MANAGER, ROLE_SUPERVISOR}) and (
            user_can_manage_health_unit(request.user, obj.health_unit_id)
        )


class ManagerOrAdminPermission(BasePermission):
    def has_permission(self, request, view):
        roles = get_user_roles(request.user)
        return bool(roles & {ROLE_ADMIN, ROLE_MANAGER})


class HealthUnitViewPermission(BasePermission):
    manager_actions = {"list", "create", "update", "partial_update", "destroy"}
    detail_read_actions = {"retrieve", "patients", "professionals"}

    def has_permission(self, request, view):
        roles = get_user_roles(request.user)
        if not roles:
            return False

        action = getattr(view, "action", None)
        if action in self.manager_actions:
            allowed = {ROLE_ADMIN, ROLE_MANAGER}
        elif action in self.detail_read_actions:
            allowed = {ROLE_ADMIN, ROLE_MANAGER, ROLE_SUPERVISOR, ROLE_PROFESSIONAL}
        else:
            allowed = {ROLE_ADMIN, ROLE_MANAGER}

        return bool(roles & allowed)

    def has_object_permission(self, request, view, obj):
        return user_can_access_health_unit(request.user, obj.pk)


class PatientViewPermission(BasePermission):
    def has_permission(self, request, view):
        roles = get_user_roles(request.user)
        if not roles:
            return False

        action = getattr(view, "action", None)
        if action == "create":
            return bool(roles & {ROLE_ADMIN, ROLE_SUPERVISOR, ROLE_PROFESSIONAL})

        return bool(roles & {ROLE_ADMIN, ROLE_MANAGER, ROLE_SUPERVISOR, ROLE_PROFESSIONAL})

    def has_object_permission(self, request, view, obj):
        return user_can_access_patient(request.user, obj.user_id)


class PatientNestedResourcePermission(BasePermission):
    read_actions = {"list", "retrieve", "needs_signature", "signed_terms", "calculate"}
    write_actions = {"create", "update", "partial_update", "sign"}

    def has_permission(self, request, view):
        roles = get_user_roles(request.user)
        if not roles:
            return False

        action = getattr(view, "action", None)
        if action in self.read_actions:
            allowed = {ROLE_ADMIN, ROLE_MANAGER, ROLE_SUPERVISOR, ROLE_PROFESSIONAL}
        elif action in self.write_actions:
            allowed = {ROLE_ADMIN, ROLE_SUPERVISOR, ROLE_PROFESSIONAL}
        else:
            allowed = {ROLE_ADMIN, ROLE_MANAGER, ROLE_SUPERVISOR, ROLE_PROFESSIONAL}

        user_pk = view.kwargs.get("user_pk")
        return bool(roles & allowed) and (
            user_pk is None or user_can_access_patient(request.user, user_pk)
        )
