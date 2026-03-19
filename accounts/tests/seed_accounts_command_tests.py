import pytest
from django.core.management import call_command
from pytest_factoryboy import register

from accounts.enums.permission_role import PermissionRole
from accounts.models import InviteWork, Patient, User, Work
from .factories import HealthUnitFactory

register(HealthUnitFactory)


@pytest.mark.django_db
class TestSeedAccountsCommand:
    def test_seed_accounts_creates_role_demo_data_and_linked_patients(
        self, health_unit_factory
    ):
        health_unit_factory.create_batch(2)

        call_command(
            "seed_accounts",
            users=4,
            patients=3,
            works=2,
            sessions=1,
            verbosity=0,
        )

        manager = User.objects.get(email="manager.seed@dermalert.local")
        supervisor = User.objects.get(email="supervisor.seed@dermalert.local")
        technician = User.objects.get(email="technician.seed@dermalert.local")
        invited_user = User.objects.get(email="invite.seed@dermalert.local")

        assert Work.objects.filter(
            user=manager,
            permission_role=PermissionRole.MANAGER,
            is_active=True,
            is_deleted=False,
        ).exists()
        assert Work.objects.filter(
            user=supervisor,
            permission_role=PermissionRole.SUPERVISOR,
            is_active=True,
            is_deleted=False,
        ).exists()
        assert Work.objects.filter(
            user=technician,
            permission_role=PermissionRole.TECHNICIAN,
            is_active=True,
            is_deleted=False,
        ).exists()

        assert (
            Patient.objects.filter(health_unit__isnull=False, is_deleted=False).count()
            >= 2
        )

        invite = InviteWork.objects.get(email="invite.seed@dermalert.local")
        assert invite.is_active is True
        assert invite.is_deleted is False
        assert invited_user.is_active is False
        assert invited_user.has_usable_password() is False
