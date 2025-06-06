# -*- coding: utf-8 -*-
"""
Management command que popula ChronicDisease, Medicine e Allergy
com listas de exemplos comuns em português.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

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


class Command(BaseCommand):
    help = "Popula ChronicDisease, Medicine e Allergy com listas padrão em português."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Iniciando seed de catálogos…"))
        with transaction.atomic():
            self._bulk_seed(ChronicDisease, CHRONIC_DISEASES, "Doenças crônicas")
            self._bulk_seed(Medicine, MEDICINES, "Medicamentos")
            self._bulk_seed(Allergy, ALLERGIES, "Alergias")
        self.stdout.write(self.style.SUCCESS("✓ Catálogos populados com sucesso!"))

    def _bulk_seed(self, model, items, label):
        created = model.objects.bulk_create(
            [model(name=name) for name in items],
            ignore_conflicts=True,
        )
        self.stdout.write(f"  • {label}: {len(created)} inseridos, "
                          f"{len(items) - len(created)} já existiam.")
