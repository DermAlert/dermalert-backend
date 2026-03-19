import hashlib
from datetime import date, timedelta

from django.utils import timezone

from core.management.commands.base_seed import BaseSeedCommand
from accounts.models import InviteWork, Patient, Session, User, Work
from accounts.enums.gender import Gender
from accounts.enums.permission_role import PermissionRole
from health_unit.models import HealthUnit
from address.models import Address

DEMO_PASSWORD = "senha123"


class Command(BaseSeedCommand):
    seed_name = "accounts"
    seed_description = "Usuários, pacientes, trabalhos e sessões"
    help = "Seed accounts app with realistic test data using Faker"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--users",
            type=int,
            default=50,
            help="Number of users to create (default: 50)",
        )
        parser.add_argument(
            "--patients",
            type=int,
            default=30,
            help="Number of patients to create (default: 30)",
        )
        parser.add_argument(
            "--works",
            type=int,
            default=20,
            help="Number of work assignments to create (default: 20)",
        )
        parser.add_argument(
            "--sessions",
            type=int,
            default=15,
            help="Number of sessions to create (default: 15)",
        )

    def handle_seed(self, fake, *args, **options):
        """Executa o seed do app accounts"""
        if not Address.objects.exists():
            self.stdout.write(
                self.style.ERROR(
                    '❌ Nenhum endereço encontrado. Execute "python manage.py seed_addresses" primeiro.'
                )
            )
            return {"erro": "Dependências não encontradas"}

        if not HealthUnit.objects.exists():
            self.stdout.write(
                self.style.ERROR(
                    '❌ Nenhuma unidade de saúde encontrada. Execute "python manage.py seed_health_units" primeiro.'
                )
            )
            return {"erro": "Dependências não encontradas"}

        health_units = list(HealthUnit.objects.order_by("id"))

        demo_data = self._create_demo_data(health_units)
        users = self._create_users(fake, options["users"])
        works = self._create_works(fake, users, options["works"], health_units)
        patients = self._create_patients(fake, users, options["patients"], health_units)
        sessions = self._create_sessions(fake, users, options["sessions"])

        self._print_demo_access(demo_data)

        return {
            "usuários": len(users) + demo_data["users_count"],
            "pacientes": len(patients) + demo_data["patients_count"],
            "trabalhos": len(works) + demo_data["works_count"],
            "sessões": len(sessions),
            "convites": demo_data["invites_count"],
        }

    def _clear_data(self, options):
        """Limpa dados existentes das tabelas do app accounts"""
        self.stdout.write("🧹 Limpando dados existentes...")

        invite_count = InviteWork.objects.count()
        session_count = Session.objects.count()
        work_count = Work.objects.count()
        patient_count = Patient.objects.count()
        user_count = User.objects.filter(is_superuser=False).count()

        InviteWork.objects.all().delete()
        Session.objects.all().delete()
        Work.objects.all().delete()
        Patient.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Dados removidos: {user_count} usuários, {patient_count} pacientes, "
                f"{work_count} trabalhos, {session_count} sessões, {invite_count} convites"
            )
        )

    def _create_users(self, fake, count):
        """Cria usuários com dados realistas"""
        self.stdout.write(f"👥 Criando {count} usuários...")

        users = []
        addresses = list(Address.objects.all())
        reserved_cpfs = set(User.objects.values_list("cpf", flat=True))

        for _ in range(count):
            cpf = self._generate_unique_cpf(fake, reserved_cpfs)
            if cpf is None:
                continue
            reserved_cpfs.add(cpf)

            user = User(
                cpf=cpf,
                name=fake.name(),
                email=(
                    f"user.{cpf}@seed.dermalert.local"
                    if fake.boolean(chance_of_getting_true=80)
                    else ""
                ),
                address=fake.random_element(addresses)
                if addresses and fake.boolean(chance_of_getting_true=70)
                else None,
                is_active=fake.boolean(chance_of_getting_true=95),
                is_staff=False,
            )
            user.set_password(DEMO_PASSWORD)
            users.append(user)

        try:
            User.objects.bulk_create(users, ignore_conflicts=True)
            created_users = User.objects.filter(cpf__in=[u.cpf for u in users])

            self.stdout.write(
                self.style.SUCCESS(f"✅ {created_users.count()} usuários criados!")
            )
            return list(created_users)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao criar usuários: {e}"))
            return []

    def _create_patients(self, fake, users, count, health_units):
        """Cria perfis de pacientes vinculados a unidades de saúde"""
        if not users:
            self.stdout.write(
                self.style.WARNING("⚠️  Nenhum usuário disponível para criar pacientes")
            )
            return []

        self.stdout.write(f"🏥 Criando {count} pacientes...")

        if count > len(users):
            count = len(users)
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  Reduzindo número de pacientes para {count} (limitado pelo número de usuários)"
                )
            )

        worker_ids = set(
            Work.objects.filter(
                user__in=users,
                is_active=True,
                is_deleted=False,
            ).values_list("user_id", flat=True)
        )
        available_users = [
            user
            for user in users
            if not hasattr(user, "patient_profile") and user.pk not in worker_ids
        ]
        if not available_users:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Todos os usuários disponíveis já estão vinculados como pacientes ou profissionais"
                )
            )
            return []

        selected_users = fake.random_elements(
            available_users,
            length=min(count, len(available_users)),
            unique=True,
        )

        patients = []
        for index, user in enumerate(selected_users):
            sus_number = str(
                fake.random_int(min=100_000_000_000_000, max=999_999_999_999_999)
            )
            max_attempts = 10
            attempts = 0
            while (
                Patient.objects.filter(sus_number=sus_number).exists()
                and attempts < max_attempts
            ):
                sus_number = str(
                    fake.random_int(min=100_000_000_000_000, max=999_999_999_999_999)
                )
                attempts += 1

            if attempts >= max_attempts:
                continue

            phone = (
                fake.phone_number()
                .replace("(", "")
                .replace(")", "")
                .replace("-", "")
                .replace(" ", "")[:15]
            )
            birth_date = fake.date_of_birth(minimum_age=0, maximum_age=100)
            gender = fake.random_element([choice[0] for choice in Gender.choices])

            patient = Patient(
                user=user,
                sus_number=sus_number,
                phone_number=phone,
                gender=gender,
                other_gender=fake.word() if gender == Gender.OTHER else None,
                date_of_birth=birth_date,
                health_unit=health_units[index % len(health_units)] if health_units else None,
            )
            patients.append(patient)

        try:
            Patient.objects.bulk_create(patients, ignore_conflicts=True)

            self.stdout.write(
                self.style.SUCCESS(f"✅ {len(patients)} pacientes criados!")
            )
            return patients
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao criar pacientes: {e}"))
            return []

    def _create_works(self, fake, users, count, health_units):
        """Cria registros de trabalho para usuários"""
        if not users:
            self.stdout.write(
                self.style.WARNING("⚠️  Nenhum usuário disponível para criar trabalhos")
            )
            return []

        self.stdout.write(f"💼 Criando {count} trabalhos...")

        if not health_units:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Nenhuma unidade de saúde disponível para criar trabalhos"
                )
            )
            return []

        active_assignment_pairs = set(
            Work.objects.filter(is_active=True, is_deleted=False).values_list(
                "user_id",
                "health_unit_id",
            )
        )
        supervisor_user_ids = set(
            Work.objects.filter(
                permission_role=PermissionRole.SUPERVISOR,
                is_active=True,
                is_deleted=False,
            ).values_list("user_id", flat=True)
        )
        available_users = [user for user in users if not hasattr(user, "patient_profile")]
        if not available_users:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Nenhum usuário disponível para criar trabalhos extras"
                )
            )
            return []

        works = []
        attempts = 0
        max_attempts = max(count * 10, 20)
        role_pool = [
            PermissionRole.TECHNICIAN,
            PermissionRole.TECHNICIAN,
            PermissionRole.TECHNICIAN,
            PermissionRole.MANAGER,
        ]

        while len(works) < count and attempts < max_attempts:
            attempts += 1
            user = fake.random_element(available_users)
            health_unit = fake.random_element(health_units)

            if (user.pk, health_unit.pk) in active_assignment_pairs:
                continue

            candidate_roles = role_pool.copy()
            if user.pk not in supervisor_user_ids:
                candidate_roles.append(PermissionRole.SUPERVISOR)

            work = Work(
                user=user,
                health_unit=health_unit,
                permission_role=fake.random_element(candidate_roles),
                start_date=fake.date_between(start_date="-1y", end_date="today"),
                end_date=None,
            )
            work.full_clean()
            works.append(work)

            active_assignment_pairs.add((user.pk, health_unit.pk))
            if work.permission_role == PermissionRole.SUPERVISOR:
                supervisor_user_ids.add(user.pk)

        try:
            Work.objects.bulk_create(works, ignore_conflicts=True)

            self.stdout.write(self.style.SUCCESS(f"✅ {len(works)} trabalhos criados!"))
            return works
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao criar trabalhos: {e}"))
            return []

    def _create_sessions(self, fake, users, count):
        """Cria sessões de trabalho para usuários"""
        if not users:
            self.stdout.write(
                self.style.WARNING("⚠️  Nenhum usuário disponível para criar sessões")
            )
            return []

        self.stdout.write(f"⏰ Criando {count} sessões...")

        worker_ids = list(
            Work.objects.filter(
                user__in=users,
                is_active=True,
                is_deleted=False,
            )
            .values_list("user_id", flat=True)
            .distinct()
        )
        session_users = [user for user in users if user.pk in worker_ids] or users

        sessions = []
        for _ in range(count):
            user = fake.random_element(session_users)

            start_hour = fake.random_int(min=6, max=18)
            start_minute = fake.random_element([0, 15, 30, 45])
            end_hour = start_hour + fake.random_int(min=1, max=8)
            if end_hour > 23:
                end_hour = 23
            end_minute = fake.random_element([0, 15, 30, 45])

            session = Session(
                user_id=user,
                start=fake.time_object().replace(hour=start_hour, minute=start_minute),
                end=fake.time_object().replace(hour=end_hour, minute=end_minute),
            )
            sessions.append(session)

        try:
            Session.objects.bulk_create(sessions, ignore_conflicts=True)

            self.stdout.write(
                self.style.SUCCESS(f"✅ {len(sessions)} sessões criadas!")
            )
            return sessions
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao criar sessões: {e}"))
            return []

    def _create_demo_data(self, health_units):
        """Cria dados previsíveis para as APIs novas."""
        primary_unit = health_units[0]
        secondary_unit = health_units[1] if len(health_units) > 1 else primary_unit

        admin_user = self._upsert_demo_user(
            cpf_seed=101,
            name="Demo Admin",
            email="admin.seed@dermalert.local",
            address=primary_unit.address,
            is_staff=True,
        )
        manager_user = self._upsert_demo_user(
            cpf_seed=102,
            name="Demo Manager",
            email="manager.seed@dermalert.local",
            address=primary_unit.address,
        )
        supervisor_user = self._upsert_demo_user(
            cpf_seed=103,
            name="Demo Supervisor",
            email="supervisor.seed@dermalert.local",
            address=primary_unit.address,
        )
        technician_user = self._upsert_demo_user(
            cpf_seed=104,
            name="Demo Technician",
            email="technician.seed@dermalert.local",
            address=primary_unit.address,
        )
        technician_user_two = self._upsert_demo_user(
            cpf_seed=105,
            name="Demo Technician Two",
            email="technician2.seed@dermalert.local",
            address=secondary_unit.address,
        )
        patient_user_one = self._upsert_demo_user(
            cpf_seed=106,
            name="Paciente Demo Um",
            email="patient1.seed@dermalert.local",
            address=primary_unit.address,
        )
        patient_user_two = self._upsert_demo_user(
            cpf_seed=107,
            name="Paciente Demo Dois",
            email="patient2.seed@dermalert.local",
            address=secondary_unit.address,
        )
        invited_user = self._upsert_demo_user(
            cpf_seed=108,
            name="Convite Demo",
            email="invite.seed@dermalert.local",
            address=secondary_unit.address,
            is_active=False,
            use_unusable_password=True,
        )

        demo_works = [
            self._upsert_work(
                user=manager_user,
                health_unit=primary_unit,
                permission_role=PermissionRole.MANAGER,
                is_active=True,
            ),
            self._upsert_work(
                user=supervisor_user,
                health_unit=primary_unit,
                permission_role=PermissionRole.SUPERVISOR,
                is_active=True,
            ),
            self._upsert_work(
                user=technician_user,
                health_unit=primary_unit,
                permission_role=PermissionRole.TECHNICIAN,
                is_active=True,
            ),
            self._upsert_work(
                user=technician_user_two,
                health_unit=secondary_unit,
                permission_role=PermissionRole.TECHNICIAN,
                is_active=True,
            ),
            self._upsert_work(
                user=invited_user,
                health_unit=secondary_unit,
                permission_role=PermissionRole.TECHNICIAN,
                is_active=False,
            ),
        ]

        demo_patients = [
            self._upsert_patient(
                user=patient_user_one,
                sus_number="700000000000001",
                phone_number="11940000001",
                date_of_birth=date(1985, 5, 10),
                health_unit=primary_unit,
                gender=Gender.FEMALE,
            ),
            self._upsert_patient(
                user=patient_user_two,
                sus_number="700000000000002",
                phone_number="11940000002",
                date_of_birth=date(1992, 8, 22),
                health_unit=secondary_unit,
                gender=Gender.MALE,
            ),
        ]

        raw_token = f"seed-registration-{self.seed_int}"
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

        InviteWork.objects.filter(user=invited_user).exclude(hash=token_hash).update(
            is_active=False,
            is_deleted=True,
        )
        invite, _ = InviteWork.objects.get_or_create(
            hash=token_hash,
            defaults={
                "user": invited_user,
                "name": invited_user.name,
                "cpf": invited_user.cpf,
                "email": invited_user.email,
                "permission_role": PermissionRole.TECHNICIAN,
                "health_unit_code": secondary_unit,
                "start_date_work": timezone.now(),
                "end_date_work": None,
                "expires_at": timezone.now() + timedelta(days=30),
            },
        )
        invite.user = invited_user
        invite.name = invited_user.name
        invite.cpf = invited_user.cpf
        invite.email = invited_user.email
        invite.permission_role = PermissionRole.TECHNICIAN
        invite.health_unit_code = secondary_unit
        invite.accepted_at = None
        invite.expires_at = timezone.now() + timedelta(days=30)
        invite.start_date_work = timezone.now()
        invite.end_date_work = None
        invite.is_active = True
        invite.is_deleted = False
        invite.save()

        return {
            "users_count": 8,
            "patients_count": len(demo_patients),
            "works_count": len(demo_works),
            "invites_count": 1,
            "admin_user": admin_user,
            "manager_user": manager_user,
            "supervisor_user": supervisor_user,
            "technician_user": technician_user,
            "raw_invite_token": raw_token,
            "secondary_unit": secondary_unit,
        }

    def _upsert_demo_user(
        self,
        *,
        cpf_seed,
        name,
        email,
        address,
        is_staff=False,
        is_active=True,
        use_unusable_password=False,
    ):
        cpf = self._build_valid_cpf(cpf_seed)
        user = User.objects.filter(cpf=cpf).first()
        if user is None:
            user = User(cpf=cpf)
        user.name = name
        user.email = email
        user.address = address
        user.is_active = is_active
        user.is_staff = is_staff
        user.is_superuser = False
        if use_unusable_password:
            user.set_unusable_password()
        else:
            user.set_password(DEMO_PASSWORD)
        user.save()
        return user

    def _upsert_work(self, *, user, health_unit, permission_role, is_active):
        work = Work.objects.filter(user=user, health_unit=health_unit).first()
        if work is None:
            work = Work(user=user, health_unit=health_unit)

        work.permission_role = permission_role
        work.start_date = timezone.localdate() - timedelta(days=30)
        work.end_date = None
        work.is_active = is_active
        work.is_deleted = False
        work.full_clean()
        work.save()
        return work

    def _upsert_patient(
        self,
        *,
        user,
        sus_number,
        phone_number,
        date_of_birth,
        health_unit,
        gender,
    ):
        patient = Patient.objects.filter(user=user).first()
        if patient is None:
            patient = Patient(user=user)
        patient.sus_number = sus_number
        patient.phone_number = phone_number
        patient.gender = gender
        patient.other_gender = None
        patient.date_of_birth = date_of_birth
        patient.health_unit = health_unit
        patient.is_active = True
        patient.is_deleted = False
        patient.save()
        return patient

    def _print_demo_access(self, demo_data):
        self.stdout.write("\n🔐 Demo access for the new APIs:")
        self.stdout.write(
            f"   Admin      CPF: {demo_data['admin_user'].cpf} | password: {DEMO_PASSWORD}"
        )
        self.stdout.write(
            f"   Manager    CPF: {demo_data['manager_user'].cpf} | password: {DEMO_PASSWORD}"
        )
        self.stdout.write(
            f"   Supervisor CPF: {demo_data['supervisor_user'].cpf} | password: {DEMO_PASSWORD}"
        )
        self.stdout.write(
            f"   Technician CPF: {demo_data['technician_user'].cpf} | password: {DEMO_PASSWORD}"
        )
        self.stdout.write(
            f"   Invite token: {demo_data['raw_invite_token']} "
            f"({demo_data['secondary_unit'].name})"
        )

    def _generate_unique_cpf(self, fake, reserved_cpfs):
        max_attempts = 20
        attempts = 0

        while attempts < max_attempts:
            cpf = fake.cpf().replace(".", "").replace("-", "")
            if cpf not in reserved_cpfs:
                return cpf
            attempts += 1

        return None

    def _build_valid_cpf(self, seed_number):
        base_digits = [int(char) for char in str(seed_number).zfill(9)[-9:]]
        first_digit = self._calculate_cpf_digit(base_digits, 10)
        second_digit = self._calculate_cpf_digit(base_digits + [first_digit], 11)
        return "".join(str(digit) for digit in base_digits + [first_digit, second_digit])

    def _calculate_cpf_digit(self, digits, weight_start):
        total = sum(
            digit * weight for digit, weight in zip(digits, range(weight_start, 1, -1))
        )
        return ((total * 10) % 11) % 10
