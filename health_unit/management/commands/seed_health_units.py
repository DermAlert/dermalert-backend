from core.management.commands.base_seed import BaseSeedCommand
from health_unit.models import HealthUnit
from address.models import Address


class Command(BaseSeedCommand):
    seed_name = "health_units"
    seed_description = "Unidades de saúde"
    help = "Seed unidades de saúde com dados realistas"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--count",
            type=int,
            default=20,
            help="Número de unidades de saúde para criar (padrão: 20)",
        )

    def handle_seed(self, fake, *args, **options):
        """Executa o seed de unidades de saúde"""
        count = options["count"]

        # Verificar se existem endereços
        if not Address.objects.exists():
            self.stdout.write(
                self.style.ERROR(
                    '❌ Nenhum endereço encontrado. Execute "python manage.py seed_addresses" primeiro.'
                )
            )
            return {"unidades de saúde": 0}

        health_units = self._create_health_units(fake, count)

        return {"unidades de saúde": health_units}

    def _clear_data(self, options):
        """Limpa unidades de saúde existentes"""
        self.stdout.write("🧹 Removendo unidades de saúde existentes...")
        deleted_count = HealthUnit.objects.count()
        HealthUnit.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f"✅ {deleted_count} unidades de saúde removidas!")
        )

    def _create_health_units(self, fake, count):
        """Cria unidades de saúde com dados realistas"""
        self.stdout.write(f"🏥 Criando {count} unidades de saúde...")

        # Tipos de unidades de saúde brasileiras
        unit_types = [
            "UBS",  # Unidade Básica de Saúde
            "ESF",  # Estratégia Saúde da Família
            "AMA",  # Assistência Médica Ambulatorial
            "CTA",  # Centro de Testagem e Aconselhamento
            "CAPS",  # Centro de Atenção Psicossocial
            "CEO",  # Centro de Especialidades Odontológicas
            "Policlínica",
            "Hospital Municipal",
            "Hospital Estadual",
            "Pronto Socorro",
            "UPA",  # Unidade de Pronto Atendimento
            "Centro de Especialidades",
            "Centro de Saúde",
            "Ambulatório de Especialidades",
        ]

        # Sufixos realistas para nomes
        name_suffixes = [
            "Central",
            "Norte",
            "Sul",
            "Leste",
            "Oeste",
            "I",
            "II",
            "III",
            "IV",
            "V",
            "Dr. José Silva",
            "Dra. Maria Santos",
            "Dr. João Oliveira",
            "Vila Nova",
            "Centro",
            "Jardim das Flores",
            "São José",
            "Santa Maria",
            "Nossa Senhora",
        ]

        addresses = list(Address.objects.all())
        if not addresses:
            self.stdout.write(self.style.ERROR("❌ Nenhum endereço disponível"))
            return 0

        health_units = []
        used_addresses = set()
        created_count = 0

        for i in range(count):
            # Selecionar endereço único
            available_addresses = [a for a in addresses if a.id not in used_addresses]
            if not available_addresses:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  Apenas {len(used_addresses)} endereços disponíveis. "
                        f"Criando {created_count} unidades de saúde."
                    )
                )
                break

            address = fake.random_element(available_addresses)
            used_addresses.add(address.id)

            # Gerar nome da unidade
            unit_type = fake.random_element(unit_types)
            suffix = fake.random_element(name_suffixes)
            unit_name = f"{unit_type} {suffix}"

            # Garantir nome único
            max_attempts = 5
            attempts = 0
            while (
                HealthUnit.objects.filter(name=unit_name).exists()
                and attempts < max_attempts
            ):
                suffix = fake.random_element(name_suffixes)
                unit_name = f"{unit_type} {suffix}"
                attempts += 1

            if attempts >= max_attempts:
                # Se não conseguir nome único, adicionar número sequencial
                unit_name = f"{unit_type} {suffix} {i + 1}"

            # Gerar email institucional
            domain_options = [
                "saude.gov.br",
                "prefeitura.sp.gov.br",
                "sus.br",
                "saude.rj.gov.br",
                "saude.mg.gov.br",
                "saude.rs.gov.br",
            ]

            email_prefix = unit_type.lower().replace(" ", ".")
            domain = fake.random_element(domain_options)
            email = f"{email_prefix}.{address.city.lower().replace(' ', '')}@{domain}"

            health_unit = HealthUnit(
                name=unit_name,
                address=address,
                email=email,
            )
            health_units.append(health_unit)
            created_count += 1

        # Usar bulk_create para performance
        try:
            HealthUnit.objects.bulk_create(health_units, ignore_conflicts=True)
            actual_created = HealthUnit.objects.filter(
                name__in=[hu.name for hu in health_units]
            ).count()

            self.stdout.write(
                self.style.SUCCESS(f"✅ {actual_created} unidades de saúde criadas!")
            )

            return actual_created

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erro ao criar unidades de saúde: {e}")
            )
            return 0
