"""Management command para popular catálogos relacionados ao FamilyHistory.

Inclui:
 - Relatives (graus/parentes de histórico familiar)
 - CancerTypes (tipos comuns de câncer)
 - InjuriesTreatment (tratamentos/remoções de lesões)

Uso:
    python manage.py seed_family_history_catalogs

Opções úteis:
    --clear        Remove todos os registros antes de inserir
    --verbose-seed Mostra detalhes de configuração do seed
"""

from core.management.commands.base_seed import BaseSeedCommand
from profile_forms.models import Relatives, CancerTypes, InjuriesTreatment


PARENTS = [
    # Parentes de primeiro e segundo grau mais usuais em anamnese oncológica
    "Mãe",
    "Pai",
    "Irmã",
    "Irmão",
    "Filha",
    "Filho",
    "Avó materna",
    "Avô materno",
    "Avó paterna",
    "Avô paterno",
    "Tia materna",
    "Tio materno",
    "Tia paterna",
    "Tio paterno",
    "Prima de primeiro grau",
    "Primo de primeiro grau",
    "Sobrinha",
    "Sobrinho",
    "Bisavó",
    "Bisavô",
    "Outros",
]

CANCER_TYPES = [
    "Melanoma",
    "Carinoma Basocelular",
    "Carinoma Espinocelular",
]

INJURIES_TREATMENTS = [
    # Tratamentos/abordagens comuns para lesões / neoplasias cutâneas
    "Cirurgia excisional",
    "Biópsia excisional",
    "Curetagem",
    "Curetagem e eletrocoagulação",
    "Crioterapia",
    "Eletrocauterização",
    "Laser",
    "Radioterapia",
    "Quimioterapia sistêmica",
    "Quimioterapia tópica",
    "Imunoterapia",
    "Terapia alvo",
    "Observação/Follow-up",
    "Outros",
]


class Command(BaseSeedCommand):
    seed_name = "family_history_catalogs"
    seed_description = "Catálogos de histórico familiar (parentes, tipos de câncer, tratamentos de lesões)"
    help = "Popula Relatives, CancerTypes e InjuriesTreatment com listas padrão."

    def handle_seed(self, fake, *args, **options):  # noqa: ARG002
        relatives = self._bulk_seed(Relatives, PARENTS, "Parentes")
        cancer_types = self._bulk_seed(CancerTypes, CANCER_TYPES, "Tipos de câncer")
        treatments = self._bulk_seed(InjuriesTreatment, INJURIES_TREATMENTS, "Tratamentos de lesões")
        return {
            "relatives": relatives,
            "cancer_types": cancer_types,
            "injuries_treatments": treatments,
        }

    def _clear_data(self, options):  # noqa: ARG002
        self.stdout.write("🧹 Removendo catálogos de histórico familiar existentes...")
        relatives_count = Relatives.objects.count()
        cancer_count = CancerTypes.objects.count()
        treatments_count = InjuriesTreatment.objects.count()
        Relatives.objects.all().delete()
        CancerTypes.objects.all().delete()
        InjuriesTreatment.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Catálogos removidos: {relatives_count} parentes, {cancer_count} tipos de câncer, {treatments_count} tratamentos"
            )
        )

    def _bulk_seed(self, model, items, label):  # noqa: D401
        """Cria itens em lote para um modelo listado."""
        self.stdout.write(f"📋 Criando {label.lower()}...")
        try:
            created_objects = model.objects.bulk_create(
                [model(name=name) for name in items],
                ignore_conflicts=True,
            )
            total_existing = model.objects.filter(name__in=items).count()
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ {label}: {total_existing} total ("
                    f"{len(created_objects)} novos, {total_existing - len(created_objects)} já existiam)"
                )
            )
            return total_existing
        except Exception as e:  # pragma: no cover - logging de erro
            self.stdout.write(
                self.style.ERROR(f"❌ Erro ao criar {label.lower()}: {e}")
            )
            return 0
