from core.management.commands.base_seed import BaseSeedCommand
from accounts.models import User, Patient, Work, Session
from accounts.enums.gender import Gender
from accounts.enums.permission_role import PermissionRole
from health_unit.models import HealthUnit
from address.models import Address
from datetime import timedelta


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
        # Verificar dependências
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

        # Criar usuários
        users = self._create_users(fake, options["users"])

        # Criar pacientes
        patients = self._create_patients(fake, users, options["patients"])

        # Criar trabalhos
        works = self._create_works(fake, users, options["works"])

        # Criar sessões
        sessions = self._create_sessions(fake, users, options["sessions"])

        return {
            "usuários": len(users),
            "pacientes": len(patients),
            "trabalhos": len(works),
            "sessões": len(sessions),
        }

    def _clear_data(self, options):
        """Limpa dados existentes das tabelas do app accounts"""
        self.stdout.write("🧹 Limpando dados existentes...")

        session_count = Session.objects.count()
        work_count = Work.objects.count()
        patient_count = Patient.objects.count()
        user_count = User.objects.filter(is_superuser=False).count()

        Session.objects.all().delete()
        Work.objects.all().delete()
        Patient.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()  # Preservar superusuários

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Dados removidos: {user_count} usuários, {patient_count} pacientes, "
                f"{work_count} trabalhos, {session_count} sessões"
            )
        )

    def _create_users(self, fake, count):
        """Cria usuários com dados realistas"""
        self.stdout.write(f"👥 Criando {count} usuários...")

        users = []
        addresses = list(Address.objects.all())

        for i in range(count):
            # Gerar CPF válido (formato simples para teste)
            cpf = fake.cpf().replace(".", "").replace("-", "")

            # Garantir que o CPF seja único
            max_attempts = 10
            attempts = 0
            while User.objects.filter(cpf=cpf).exists() and attempts < max_attempts:
                cpf = fake.cpf().replace(".", "").replace("-", "")
                attempts += 1

            if attempts >= max_attempts:
                continue  # Pular se não conseguir CPF único

            user = User(
                cpf=cpf,
                name=fake.name(),
                email=fake.email() if fake.boolean(chance_of_getting_true=80) else "",
                address=fake.random_element(addresses)
                if addresses and fake.boolean(chance_of_getting_true=70)
                else None,
                is_active=fake.boolean(chance_of_getting_true=95),
                is_staff=fake.boolean(chance_of_getting_true=10),
            )
            user.set_password("senha123")  # Senha padrão para testes
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

    def _create_patients(self, fake, users, count):
        """Cria perfis de pacientes para alguns usuários"""
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

        # Selecionar usuários aleatórios que ainda não são pacientes
        available_users = [u for u in users if not hasattr(u, "patient_profile")]
        if not available_users:
            self.stdout.write(
                self.style.WARNING("⚠️  Todos os usuários já são pacientes")
            )
            return []

        selected_users = fake.random_elements(
            available_users, length=min(count, len(available_users)), unique=True
        )

        patients = []
        for user in selected_users:
            # Gerar número SUS único
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
                continue  # Pular se não conseguir SUS único

            # Gerar telefone
            phone = (
                fake.phone_number()
                .replace("(", "")
                .replace(")", "")
                .replace("-", "")
                .replace(" ", "")[:15]
            )

            # Data de nascimento realista
            birth_date = fake.date_of_birth(minimum_age=0, maximum_age=100)

            patient = Patient(
                user=user,
                sus_number=sus_number,
                phone_number=phone,
                gender=fake.random_element([choice[0] for choice in Gender.choices]),
                other_gender=fake.word()
                if fake.boolean(chance_of_getting_true=5)
                else None,
                date_of_birth=birth_date,
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

    def _create_works(self, fake, users, count):
        """Cria registros de trabalho para usuários"""
        if not users:
            self.stdout.write(
                self.style.WARNING("⚠️  Nenhum usuário disponível para criar trabalhos")
            )
            return []

        self.stdout.write(f"💼 Criando {count} trabalhos...")

        health_units = list(HealthUnit.objects.all())
        if not health_units:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Nenhuma unidade de saúde disponível para criar trabalhos"
                )
            )
            return []

        works = []
        for i in range(count):
            user = fake.random_element(users)
            health_unit = fake.random_element(health_units)

            # Evitar duplicatas de usuário + unidade de saúde
            if Work.objects.filter(user=user, health_unit=health_unit).exists():
                continue

            # Datas de trabalho realistas
            start_date = fake.date_between(start_date="-2y", end_date="today")
            end_date = fake.date_between(
                start_date=start_date, end_date=start_date + timedelta(days=365 * 2)
            )

            work = Work(
                user=user,
                health_unit=health_unit,
                permission_role=fake.random_element(
                    [choice[0] for choice in PermissionRole.choices]
                ),
                start_date=start_date,
                end_date=end_date,
            )
            works.append(work)

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

        sessions = []
        for i in range(count):
            user = fake.random_element(users)

            # Horários de trabalho realistas
            start_hour = fake.random_int(min=6, max=18)  # 6h às 18h
            start_minute = fake.random_element([0, 15, 30, 45])

            end_hour = start_hour + fake.random_int(
                min=1, max=8
            )  # 1 a 8 horas de trabalho
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
