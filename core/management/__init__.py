"""
Configuração central para gerenciamento de seeds do projeto DermAlert.

Este módulo define a ordem de execução dos seeds e suas dependências,
permitindo que novos seeds sejam facilmente adicionados ao sistema.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SeedConfig:
    """Configuração de um comando de seed."""

    name: str
    command: str
    description: str
    dependencies: List[str] = None
    priority: int = 100  # Menor valor = maior prioridade
    default_args: Dict[str, any] = None
    required_models: List[str] = None  # Modelos que devem existir antes de executar

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.default_args is None:
            self.default_args = {}
        if self.required_models is None:
            self.required_models = []


# Configuração de todos os seeds do projeto
# A ordem é determinada pelo campo 'priority' (menor valor = executa primeiro)
SEED_CONFIGS = [
    SeedConfig(
        name="basic_data",
        command="seed_basic_data",
        description="Dados básicos (endereços e unidades de saúde)",
        priority=10,
        default_args={"addresses": 20, "health_units": 5},
    ),
    SeedConfig(
        name="health_catalogs",
        command="seed_health_catalogs",
        description="Catálogos de saúde (doenças, medicamentos, alergias)",
        priority=20,
        dependencies=["basic_data"],
    ),
    SeedConfig(
        name="accounts",
        command="seed_accounts",
        description="Dados do app accounts (usuários, pacientes, trabalhos)",
        priority=30,
        dependencies=["basic_data", "health_catalogs"],
        default_args={"users": 50, "patients": 30, "works": 20, "sessions": 15},
        required_models=["address.Address", "health_unit.HealthUnit"],
    ),
    # Adicione novos seeds aqui seguindo o padrão
    # SeedConfig(
    #     name="skin_conditions",
    #     command="seed_skin_conditions",
    #     description="Dados de condições dermatológicas",
    #     priority=40,
    #     dependencies=["accounts"],
    #     default_args={"conditions": 20}
    # ),
]


def get_seed_configs() -> List[SeedConfig]:
    """Retorna lista de configs ordenada por prioridade."""
    return sorted(SEED_CONFIGS, key=lambda x: x.priority)


def get_seed_config(name: str) -> Optional[SeedConfig]:
    """Retorna config de um seed específico."""
    for config in SEED_CONFIGS:
        if config.name == name:
            return config
    return None


def get_execution_order(requested_seeds: List[str] = None) -> List[SeedConfig]:
    """
    Retorna a ordem de execução dos seeds considerando dependências.

    Args:
        requested_seeds: Lista de seeds específicos para executar.
                        Se None, retorna todos os seeds.
    """
    configs = get_seed_configs()

    if requested_seeds is None:
        return configs

    # Filtrar apenas os seeds solicitados e suas dependências
    selected_configs = []
    processed = set()

    def add_with_dependencies(seed_name: str):
        if seed_name in processed:
            return

        config = get_seed_config(seed_name)
        if not config:
            return

        # Adicionar dependências primeiro
        for dep in config.dependencies:
            add_with_dependencies(dep)

        if config not in selected_configs:
            selected_configs.append(config)
        processed.add(seed_name)

    for seed_name in requested_seeds:
        add_with_dependencies(seed_name)

    return sorted(selected_configs, key=lambda x: x.priority)


def validate_seed_availability() -> Dict[str, bool]:
    """
    Verifica quais comandos de seed estão disponíveis no sistema.

    Returns:
        Dict com nome do seed e se está disponível (True/False)
    """
    from django.core.management import get_commands

    available_commands = get_commands()
    availability = {}

    for config in SEED_CONFIGS:
        availability[config.name] = config.command in available_commands

    return availability
