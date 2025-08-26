import hashlib
import random
from typing import Dict, Any
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from faker import Faker


class BaseSeedCommand(BaseCommand):
    """
    Classe base para comandos de seed que padroniza:
    - Configuração do Faker com seed determinístico
    - Argumentos comuns (--clear, --verbose)
    - Estrutura de output padronizada
    - Transações automáticas
    """

    # Configurações que devem ser sobrescritas nas classes filhas
    seed_name = "base"
    seed_description = "Base seed command"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = None
        self.seed_int = None

    def add_arguments(self, parser):
        """Adiciona argumentos base. Classes filhas devem chamar super().add_arguments(parser)"""
        parser.add_argument(
            "--clear", action="store_true", help="Clear existing data before seeding"
        )
        parser.add_argument(
            "--verbose-seed", action="store_true", help="Show detailed seed information"
        )

    def handle(self, *args, **options):
        """Handle principal que configura o ambiente e chama handle_seed()"""
        self._setup_seed()

        if options.get("verbose_seed"):
            self._print_seed_info()

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"🌱 {self.seed_description} (seed: {self.seed_int})"
            )
        )

        if options.get("clear"):
            self._clear_data(options)

        with transaction.atomic():
            result = self.handle_seed(self.fake, *args, **options)

        self._print_success(result)
        # Não retornar o resultado, pois o Django espera uma string ou None
        return None

    def handle_seed(self, fake, *args, **options):
        """
        Método que deve ser implementado pelas classes filhas.
        Recebe o objeto fake configurado como primeiro parâmetro.
        Retorna um dicionário com estatísticas do seed.
        """
        raise NotImplementedError(
            "Classes filhas devem implementar handle_seed(fake, *args, **options)"
        )

    def _setup_seed(self):
        """Configura o Faker com seed determinístico baseado no SECRET_KEY"""
        seed_source = settings.SECRET_KEY[:32]
        seed_hash = hashlib.md5(seed_source.encode()).hexdigest()
        self.seed_int = int(seed_hash[:8], 16)

        # Configurar Faker e random
        self.fake = Faker("pt_BR")
        Faker.seed(self.seed_int)
        random.seed(self.seed_int)

    def _print_seed_info(self):
        """Imprime informações detalhadas do seed"""
        self.stdout.write(
            f"🔧 Seed Configuration:\n"
            f"   📛 Name: {self.seed_name}\n"
            f"   🌱 Seed: {self.seed_int}\n"
            f"   🔑 Source: {settings.SECRET_KEY[:10]}...\n"
            f"   🌍 Locale: pt_BR\n"
        )

    def _clear_data(self, options):
        """
        Método para limpeza de dados. Deve ser implementado pelas classes filhas se necessário.
        """
        self.stdout.write("🧹 Limpeza de dados não implementada para este seed.")

    def _print_success(self, result: Dict[str, Any]):
        """Imprime mensagem de sucesso com estatísticas"""
        if not isinstance(result, dict):
            result = {"items": "unknown"}

        stats = []
        for key, value in result.items():
            if isinstance(value, (int, list)):
                count = len(value) if isinstance(value, list) else value
                stats.append(f"   📊 {key.replace('_', ' ').title()}: {count}")

        stats_str = "\n".join(stats) if stats else "   📊 Seed concluído"

        self.stdout.write(
            self.style.SUCCESS(f"✅ {self.seed_description} concluído!\n{stats_str}")
        )

    def bulk_create_with_progress(
        self, model, objects, batch_size=1000, ignore_conflicts=True
    ):
        """
        Método helper para bulk_create com feedback de progresso.
        """
        if not objects:
            return []

        total = len(objects)
        created_objects = []

        for i in range(0, total, batch_size):
            batch = objects[i : i + batch_size]
            created_batch = model.objects.bulk_create(
                batch, ignore_conflicts=ignore_conflicts, batch_size=batch_size
            )
            created_objects.extend(created_batch)

            if total > batch_size:
                progress = min(i + batch_size, total)
                self.stdout.write(f"    📦 Processados {progress}/{total} itens...")

        return created_objects

    def get_or_create_with_progress(self, model, data_list, unique_field):
        """
        Método helper para get_or_create com feedback de progresso.
        """
        created_objects = []
        updated_count = 0

        for i, data in enumerate(data_list, 1):
            obj, created = model.objects.get_or_create(
                **{unique_field: data[unique_field]}, defaults=data
            )

            if created:
                created_objects.append(obj)
            else:
                updated_count += 1

            if i % 100 == 0 or i == len(data_list):
                self.stdout.write(f"    🔄 Processados {i}/{len(data_list)} itens...")

        return created_objects, updated_count
