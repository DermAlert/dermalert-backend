# 🌱 Sistema de Seeds Modularizado - DermAlert

Este projeto implementa um sistema de seeds modularizado que segue as melhores práticas do Django, organizando cada responsabilidade em seu próprio app.

## 📁 Estrutura Modularizada

### 🏗️ Apps e seus Seeds

```
core/
├── seed_config.py          # Configuração central de todos os seeds
├── management/commands/
    ├── base_seed.py        # Classe base para todos os seeds
    └── seed_all.py         # Comando principal que executa todos os seeds

address/
├── management/commands/
    └── seed_addresses.py   # 📍 Seeds de endereços brasileiros

health_unit/
├── management/commands/
    └── seed_health_units.py # 🏥 Seeds de unidades de saúde

profile_forms/
├── management/commands/
    └── seed_health_catalogs.py # 📋 Catálogos de saúde

accounts/
├── management/commands/
    └── seed_accounts.py    # 👥 Usuários, pacientes, trabalhos, sessões
```

## 🎯 Comandos Disponíveis

### 1. **`seed_all`** - Comando Principal
Executa todos os seeds automaticamente na ordem correta, respeitando dependências.

```bash
# Seed completo
uv run manage.py seed_all

# Ver seeds disponíveis e ordem de execução
uv run manage.py seed_all --list

# Limpar dados existentes e recriar
uv run manage.py seed_all --clear

# Executar apenas seeds específicos (dependências incluídas automaticamente)
uv run manage.py seed_all --only seed_addresses seed_health_units

# Pular seeds específicos
uv run manage.py seed_all --skip seed_health_catalogs

# Personalizar quantidades
uv run manage.py seed_all --users 100 --addresses 80 --health-units 15
```

### 2. **Seeds Individuais por App**

#### 📍 **Endereços** (`address` app)
```bash
uv run manage.py seed_addresses --count 50 --clear
```

#### 🏥 **Unidades de Saúde** (`health_unit` app)
```bash
uv run manage.py seed_health_units --count 20 --clear
```

#### 📋 **Catálogos de Saúde** (`profile_forms` app)
```bash
uv run manage.py seed_health_catalogs --clear
```

#### 👥 **Accounts** (`accounts` app)
```bash
uv run manage.py seed_accounts --users 100 --patients 70 --works 50 --sessions 30 --clear
```

## 🔗 Sistema de Dependências

O sistema resolve dependências automaticamente:

```
seed_addresses (sem dependências)
├── seed_health_units (depende de addresses)
└── seed_accounts (depende de addresses + health_units)

seed_health_catalogs (sem dependências)
```

## 🛠️ Configuração Central

### `/core/seed_config.py`
Arquivo que centraliza toda a configuração dos seeds:

```python
SEED_COMMANDS = {
    'seed_addresses': {
        'app': 'address',
        'dependencies': [],
        'description': 'Endereços',
        'priority': 10
    },
    'seed_health_units': {
        'app': 'health_unit', 
        'dependencies': ['seed_addresses'],
        'description': 'Unidades de saúde',
        'priority': 20
    },
    # ...
}
```

## 🏗️ Classe Base

### `/core/management/commands/base_seed.py`
Todos os seeds herdam de `BaseSeedCommand` que fornece:

- ✅ Seed determinístico baseado no SECRET_KEY
- ✅ Configuração automática do Faker (pt_BR)
- ✅ Transações automáticas
- ✅ Tratamento de erros padronizado
- ✅ Output formatado e colorido
- ✅ Argumentos comuns (--clear)

```python
class Command(BaseSeedCommand):
    seed_name = "meu_seed"
    seed_description = "Descrição do seed"
    
    def handle_seed(self, fake, *args, **options):
        # Implementar lógica do seed
        return {"items_criados": 10}
    
    def _clear_data(self, options):
        # Implementar limpeza (opcional)
        pass
```

## 🔧 Uso via Makefile

```bash
# Docker
make seed              # Seed completo
make seed-clear        # Com limpeza
make seed-list         # Listar seeds
make seed-basic        # Apenas dados básicos

# Local
make seed-local        # Seed completo local
make seed-local-clear  # Com limpeza local
make seed-local-list   # Listar seeds local
```

## 📊 Dados Gerados

### 📍 **Endereços** (50 por padrão)
- CEPs brasileiros válidos
- Estados populosos (SP, RJ, MG, etc.)
- Coordenadas dentro do território brasileiro
- Endereços únicos (CEP + número)

### 🏥 **Unidades de Saúde** (20 por padrão)
- Tipos realistas: UBS, ESF, AMA, CAPS, CEO, etc.
- Nomes institucionais brasileiros
- Emails governamentais (.gov.br, .sus.br)
- Vinculadas a endereços únicos

### 📋 **Catálogos de Saúde**
- **40 Doenças Crônicas** (diabetes, hipertensão, etc.)
- **50 Medicamentos** (paracetamol, insulina, etc.)
- **30 Alergias** (leite, amendoim, látex, etc.)

### 👥 **Accounts** (50 usuários por padrão)
- **Usuários**: CPF válido, nomes brasileiros, emails opcionais
- **Pacientes**: Número SUS, telefones, gêneros, datas de nascimento
- **Trabalhos**: Relacionamentos usuário-unidade com períodos
- **Sessões**: Horários de trabalho realistas (6h-23h)

## 🌱 Seed Determinístico

### Como Funciona
```python
seed_source = settings.SECRET_KEY[:32]
seed_hash = hashlib.md5(seed_source.encode()).hexdigest()
seed_int = int(seed_hash[:8], 16)
```

### Vantagens
- ✅ **Reprodutível**: Mesmos dados sempre
- ✅ **Ambiente-específico**: SECRET_KEY diferente = dados diferentes
- ✅ **Testável**: Dados consistentes para testes
- ✅ **Debugável**: Mesmo cenário sempre

### Alterando os Dados
Para gerar dados diferentes, altere o SECRET_KEY:
```env
DJANGO_SECRET_KEY=nova-chave-para-dados-diferentes
```

## 🚀 Adicionando Novos Seeds

### 1. Criar comando no app apropriado
```python
# meu_app/management/commands/seed_meu_modelo.py
from core.management.commands.base_seed import BaseSeedCommand

class Command(BaseSeedCommand):
    seed_name = "meu_modelo"
    seed_description = "Descrição do que faz"
    
    def handle_seed(self, fake, *args, **options):
        # Implementar lógica
        return {"criados": 10}
```

### 2. Registrar no seed_config.py
```python
SEED_COMMANDS = {
    # ...seeds existentes...
    'seed_meu_modelo': {
        'app': 'meu_app',
        'dependencies': ['seed_addresses'],  # se necessário
        'description': 'Meu modelo',
        'priority': 50
    }
}
```

### 3. Usar automaticamente
```bash
uv run manage.py seed_all  # Inclui o novo seed automaticamente
```

## 🧪 Uso em Testes

```python
# conftest.py
import pytest
from django.core.management import call_command

@pytest.fixture
def seeded_data():
    call_command('seed_all', '--users', '10', '--addresses', '5')
    
def test_com_dados(seeded_data):
    # Teste com dados seedados
    pass
```

## 🔧 Troubleshooting

### "Comando não encontrado"
- Verifique se o app está em `INSTALLED_APPS`
- Confirme que `management/commands/` existe com `__init__.py`

### "Dependência não encontrada"
```bash
python manage.py seed_all --list  # Ver ordem de execução
python manage.py seed_addresses  # Executar dependência primeiro
```

### "Dados sempre iguais"
- Isso é esperado! Para dados diferentes, altere o SECRET_KEY

### Performance lenta
- Use quantidades menores: `--users 10 --addresses 5`
- Execute seeds individuais conforme necessário

## 💡 Boas Práticas

### ✅ **Faça**
- Herde sempre de `BaseSeedCommand`
- Use dependências para ordem correta
- Implemente `_clear_data` se suportar limpeza
- Trate erros graciosamente
- Use bulk_create para performance

### ❌ **Evite**
- Seeds em produção sem cuidado extremo
- Dependências circulares
- Hardcoding de IDs ou PKs
- Seeds muito lentos (use quantidades razoáveis)
