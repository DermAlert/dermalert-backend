# -*- coding: utf-8 -*-
"""
Management command que popula ChronicDisease, Medicine e Allergy
com listas de exemplos comuns em português.
"""

from core.management.commands.base_seed import BaseSeedCommand
from profile_forms.models import ChronicDisease, Medicine, Allergy


CHRONIC_DISEASES = [
    # 40 exemplos frequentes
    "Hipertensão arterial",
    "Diabetes mellitus tipo 1",
    "Diabetes mellitus tipo 2",
    "Asma brônquica",
    "Doença pulmonar obstrutiva crônica (DPOC)",
    "Insuficiência cardíaca",
    "Doença arterial coronariana",
    "Arritmia cardíaca",
    "Doença renal crônica",
    "Doença hepática crônica",
    "Doença de Alzheimer",
    "Doença de Parkinson",
    "Artrite reumatoide",
    "Osteoartrite",
    "Lúpus eritematoso sistêmico",
    "Esclerose múltipla",
    "Hipotireoidismo",
    "Hipertireoidismo",
    "Doença celíaca",
    "Fibrose cística",
    "Fibromialgia",
    "Depressão maior",
    "Transtorno bipolar",
    "Transtorno de ansiedade generalizada",
    "Epilepsia",
    "Doença de Crohn",
    "Retocolite ulcerativa",
    "Gota",
    "Anemia falciforme",
    "Talassemia",
    "Hemofilia",
    "HIV/Aids",
    "Câncer de mama (crônico)",
    "Câncer de próstata (crônico)",
    "Câncer colorretal (crônico)",
    "Esôfago de Barrett",
    "Doença arterial periférica",
    "Glaucoma",
    "Catarata",
    "Psoríase",
]

MEDICINES = [
    # 50 fármacos largamente prescritos no Brasil
    "Paracetamol",
    "Dipirona sódica",
    "Ibuprofeno",
    "Ácido acetilsalicílico",
    "Amoxicilina",
    "Azitromicina",
    "Cefalexina",
    "Ciprofloxacino",
    "Metformina",
    "Glibenclamida",
    "Insulina humana NPH",
    "Insulina glargina",
    "Enalapril",
    "Losartana potássica",
    "Atenolol",
    "Amlodipino",
    "Furosemida",
    "Hidroclorotiazida",
    "Sinvastatina",
    "Rosuvastatina",
    "Omeprazol",
    "Pantoprazol",
    "Ranitidina",
    "Salbutamol (aerossol)",
    "Budesonida + formoterol",
    "Beclometasona",
    "Prednisona",
    "Hidrocortisona",
    "Loratadina",
    "Cetirizina",
    "Desloratadina",
    "Nimesulida",
    "Diclofenaco sódico",
    "Celecoxibe",
    "Clopidogrel",
    "Varfarina sódica",
    "Heparina",
    "Sertralina",
    "Fluoxetina",
    "Citalopram",
    "Risperidona",
    "Quetiapina",
    "Haloperidol",
    "Carbamazepina",
    "Fenitoína",
    "Ácido valpróico",
    "Levodopa + benserazida",
    "Alendronato de sódio",
    "Colecalciferol (vitamina D)",
]

ALLERGIES = [
    # 30 alérgenos ou grupos de alérgenos comuns
    "Leite de vaca",
    "Ovo",
    "Amendoim",
    "Soja",
    "Trigo/glúten",
    "Frutos do mar",
    "Crustáceos",
    "Peixes",
    "Nozes",
    "Castanha de caju",
    "Castanha do Brasil",
    "Pistache",
    "Amêndoa",
    "Látex",
    "Penicilina",
    "Cefalosporinas",
    "Sulfametoxazol-trimetoprim",
    "Nimesulida",
    "Ácido acetilsalicílico (AAS)",
    "Dipirona",
    "Corantes alimentares",
    "Conservantes (sulfitos)",
    "Ácaros",
    "Pólen",
    "Pelos de gato",
    "Pelos de cachorro",
    "Fungos (mofo)",
    "Picada de abelha",
    "Picada de formiga (fogo)",
    "Níquel",
]


class Command(BaseSeedCommand):
    seed_name = "health_catalogs"
    seed_description = "Catálogos de saúde (doenças, medicamentos, alergias)"
    help = "Popula ChronicDisease, Medicine e Allergy com listas padrão em português."

    def handle_seed(self, fake, *args, **options):
        """Executa o seed dos catálogos de saúde"""
        chronic_diseases = self._bulk_seed(
            ChronicDisease, CHRONIC_DISEASES, "Doenças crônicas"
        )
        medicines = self._bulk_seed(Medicine, MEDICINES, "Medicamentos")
        allergies = self._bulk_seed(Allergy, ALLERGIES, "Alergias")

        return {
            "doenças crônicas": chronic_diseases,
            "medicamentos": medicines,
            "alergias": allergies,
        }

    def _clear_data(self, options):
        """Limpa catálogos existentes"""
        self.stdout.write("🧹 Removendo catálogos existentes...")

        chronic_count = ChronicDisease.objects.count()
        medicine_count = Medicine.objects.count()
        allergy_count = Allergy.objects.count()

        ChronicDisease.objects.all().delete()
        Medicine.objects.all().delete()
        Allergy.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Catálogos removidos: {chronic_count} doenças, "
                f"{medicine_count} medicamentos, {allergy_count} alergias"
            )
        )

    def _bulk_seed(self, model, items, label):
        """Cria itens em lote para um modelo específico"""
        self.stdout.write(f"📋 Criando {label.lower()}...")

        try:
            created_objects = model.objects.bulk_create(
                [model(name=name) for name in items],
                ignore_conflicts=True,
            )

            # Contar quantos realmente foram criados
            total_existing = model.objects.filter(name__in=items).count()

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ {label}: {total_existing} total "
                    f"({len(created_objects)} novos, {total_existing - len(created_objects)} já existiam)"
                )
            )

            return total_existing

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erro ao criar {label.lower()}: {e}")
            )
            return 0
