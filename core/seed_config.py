"""
Configuração central para todos os comandos de seed do projeto.
Define a ordem de execução e dependências entre seeds.
"""

# Configuração dos seeds e suas dependências
# Formato: 'nome_do_comando': {'app': 'nome_do_app', 'dependencies': ['dependencia1', 'dependencia2']}
SEED_COMMANDS = {
    # Dados básicos - sem dependências
    "seed_addresses": {
        "app": "address",
        "dependencies": [],
        "description": "Endereços",
        "priority": 10,
    },
    "seed_health_units": {
        "app": "health_unit",
        "dependencies": ["seed_addresses"],
        "description": "Unidades de saúde",
        "priority": 20,
    },
    "seed_health_catalogs": {
        "app": "profile_forms",
        "dependencies": [],
        "description": "Catálogos de saúde (doenças, medicamentos, alergias)",
        "priority": 30,
    },
    "seed_family_history_catalogs": {
        "app": "profile_forms",
        "dependencies": [],
        "description": "Catálogos de histórico familiar (parentes, tipos de câncer, tratamentos de lesões)",
        "priority": 30,
    },
    # App accounts - depende dos dados básicos
    "seed_accounts": {
        "app": "accounts",
        "dependencies": ["seed_addresses", "seed_health_units"],
        "description": "Usuários, pacientes, trabalhos e sessões",
        "priority": 40,
    },
    # Futuros seeds podem ser adicionados aqui seguindo o padrão
    # 'seed_consultations': {
    #     'app': 'consultations',
    #     'dependencies': ['seed_accounts'],
    #     'description': 'Consultas médicas',
    #     'priority': 50
    # },
}


def get_seed_execution_order():
    """
    Retorna a ordem de execução dos seeds baseada em dependências e prioridade.
    """
    # Ordenar por prioridade
    ordered_seeds = sorted(SEED_COMMANDS.items(), key=lambda x: x[1]["priority"])

    return [seed_name for seed_name, config in ordered_seeds]


def get_dependencies(seed_name):
    """Retorna as dependências de um seed específico"""
    return SEED_COMMANDS.get(seed_name, {}).get("dependencies", [])


def get_seed_info(seed_name):
    """Retorna informações completas de um seed"""
    return SEED_COMMANDS.get(seed_name, {})


def get_available_seeds():
    """Retorna lista de todos os seeds disponíveis"""
    return list(SEED_COMMANDS.keys())


def validate_seed_dependencies():
    """
    Valida se todas as dependências declaradas existem como seeds válidos.
    Retorna True se válido, lista de erros caso contrário.
    """
    errors = []
    available_seeds = set(SEED_COMMANDS.keys())

    for seed_name, config in SEED_COMMANDS.items():
        for dependency in config.get("dependencies", []):
            if dependency not in available_seeds:
                errors.append(
                    f"Seed '{seed_name}' tem dependência inválida: '{dependency}'"
                )

    return True if not errors else errors
