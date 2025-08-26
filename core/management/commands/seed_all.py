from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from core.seed_config import (
    get_seed_execution_order,
    get_dependencies,
    get_seed_info,
    validate_seed_dependencies,
)
import hashlib


class Command(BaseCommand):
    help = "Execute all seed commands in the correct order with dependency resolution"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear", action="store_true", help="Clear existing data before seeding"
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="List all available seeds and their execution order",
        )
        parser.add_argument(
            "--only",
            nargs="+",
            help="Run only specific seeds (dependencies will be included automatically)",
        )
        parser.add_argument(
            "--skip", nargs="+", help="Skip specific seeds during execution"
        )

        # Argumentos para personalizar quantidades
        parser.add_argument(
            "--users",
            type=int,
            default=50,
            help="Number of users to create (default: 50)",
        )
        parser.add_argument(
            "--addresses",
            type=int,
            default=50,
            help="Number of addresses to create (default: 50)",
        )
        parser.add_argument(
            "--health-units",
            type=int,
            default=20,
            help="Number of health units to create (default: 20)",
        )

    def handle(self, *args, **options):
        # Gerar seed para exibição
        seed_source = settings.SECRET_KEY[:32]
        seed_hash = hashlib.md5(seed_source.encode()).hexdigest()
        seed_int = int(seed_hash[:8], 16)

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"🚀 Executando seed completo do projeto DermAlert\n"
                f"🌱 Seed determinístico: {seed_int}\n"
                f"{'=' * 60}"
            )
        )

        # Validar configuração de seeds
        validation_result = validate_seed_dependencies()
        if validation_result is not True:
            for error in validation_result:
                self.stdout.write(self.style.ERROR(f"❌ {error}"))
            return

        # Listar seeds se solicitado
        if options["list"]:
            self._list_seeds()
            return

        try:
            # Determinar quais seeds executar
            seeds_to_run = self._determine_seeds_to_run(options)

            # Executar seeds na ordem correta
            self._execute_seeds(seeds_to_run, options, seed_int)

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n{'=' * 60}\n"
                    f"🎉 Seed completo executado com sucesso!\n"
                    f"💡 Para recriar os mesmos dados, mantenha o mesmo SECRET_KEY\n"
                    f"🔧 Para dados diferentes, altere o SECRET_KEY"
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"❌ Erro durante o seed: {e}\n"
                    f"💡 Verifique se todas as migrações foram aplicadas: "
                    f"python manage.py migrate"
                )
            )
            raise

    def _list_seeds(self):
        """Lista todos os seeds disponíveis e sua ordem de execução"""
        execution_order = get_seed_execution_order()

        self.stdout.write(
            self.style.HTTP_INFO("\n📋 Seeds disponíveis (em ordem de execução):")
        )

        for i, seed_name in enumerate(execution_order, 1):
            seed_info = get_seed_info(seed_name)
            dependencies = get_dependencies(seed_name)

            deps_text = (
                f" (depende de: {', '.join(dependencies)})"
                if dependencies
                else " (sem dependências)"
            )

            self.stdout.write(
                f"   {i:2d}. {seed_name:<20} - {seed_info.get('description', 'N/A')}{deps_text}"
            )

        self.stdout.write("")

    def _determine_seeds_to_run(self, options):
        """Determina quais seeds executar baseado nas opções"""
        all_seeds = get_seed_execution_order()

        if options.get("only"):
            # Executar apenas seeds específicos (incluindo dependências)
            requested_seeds = set(options["only"])
            seeds_with_deps = set()

            for seed in requested_seeds:
                if seed not in all_seeds:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  Seed desconhecido: {seed}")
                    )
                    continue

                seeds_with_deps.add(seed)
                # Adicionar dependências recursivamente
                self._add_dependencies(seed, seeds_with_deps, all_seeds)

            # Filtrar e ordenar
            seeds_to_run = [seed for seed in all_seeds if seed in seeds_with_deps]
        else:
            # Executar todos os seeds
            seeds_to_run = all_seeds.copy()

        # Remover seeds que devem ser pulados
        if options.get("skip"):
            for seed in options["skip"]:
                if seed in seeds_to_run:
                    seeds_to_run.remove(seed)
                    self.stdout.write(self.style.WARNING(f"⚠️  Pulando seed: {seed}"))

        return seeds_to_run

    def _add_dependencies(self, seed_name, seeds_set, all_seeds):
        """Adiciona dependências de um seed recursivamente"""
        dependencies = get_dependencies(seed_name)
        for dep in dependencies:
            if dep in all_seeds and dep not in seeds_set:
                seeds_set.add(dep)
                self._add_dependencies(dep, seeds_set, all_seeds)

    def _execute_seeds(self, seeds_to_run, options, seed_int):
        """Executa os seeds na ordem determinada"""
        self.stdout.write(
            self.style.HTTP_INFO(f"\n🎯 Executando {len(seeds_to_run)} seeds...\n")
        )

        for i, seed_name in enumerate(seeds_to_run, 1):
            seed_info = get_seed_info(seed_name)

            self.stdout.write(
                self.style.HTTP_INFO(
                    f"📋 Etapa {i}/{len(seeds_to_run)}: {seed_info.get('description', seed_name)}"
                )
            )

            # Preparar argumentos específicos para o seed
            seed_args = self._prepare_seed_arguments(seed_name, options)

            try:
                call_command(seed_name, **seed_args)
                self.stdout.write("")  # Linha em branco para separar

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Erro ao executar {seed_name}: {e}")
                )
                raise

    def _prepare_seed_arguments(self, seed_name, options):
        """Prepara argumentos específicos para cada seed"""
        args = {}

        # Argumentos comuns
        if options.get("clear"):
            args["clear"] = True

        # Argumentos específicos por seed
        if seed_name == "seed_addresses":
            args["count"] = options.get("addresses", 50)

        elif seed_name == "seed_health_units":
            args["count"] = options.get("health_units", 20)

        elif seed_name == "seed_accounts":
            args["users"] = options.get("users", 50)
            args["patients"] = min(
                options.get("users", 50), 30
            )  # Máximo de 30 pacientes

        # Adicionar verbosity padrão
        args["verbosity"] = 1

        return args
