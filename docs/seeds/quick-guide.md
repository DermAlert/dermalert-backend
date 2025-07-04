# 🚀 Guia Prático de Seeds - DermAlert

Este é um guia rápido com exemplos práticos para usar o sistema de seeds modularizado.

## ⚡ Comandos Mais Usados

### Desenvolvimento Diário
```bash
# Setup inicial - executar uma vez
uv run manage.py migrate
uv run manage.py seed_all --users 20 --addresses 30 --health-units 5

# Reset rápido para testes
uv run manage.py seed_all --clear --users 10 --addresses 15
```

### Via Makefile (Docker)
```bash
make seed              # Seed completo
make seed-clear        # Com limpeza
make seed-list         # Ver seeds disponíveis
make seed-basic        # Apenas endereços + unidades de saúde
```

### Via Makefile (Local)
```bash
make seed-local        # Seed completo local
make seed-local-clear  # Com limpeza local
```

## 🎯 Cenários Específicos

### 1. Apenas Dados Básicos
```bash
# Para quando você só precisa de endereços e unidades de saúde
uv run manage.py seed_all --only seed_addresses seed_health_units

# Ou especificando quantidades
uv run manage.py seed_addresses --count 20
uv run manage.py seed_health_units --count 5
```

### 2. Desenvolvimento de Features de Usuários
```bash
# Foco em usuários e pacientes
uv run manage.py seed_all --only seed_accounts --users 30
```

### 3. Testes de Performance
```bash
# Quantidades maiores para teste de performance
uv run manage.py seed_all --users 500 --addresses 200 --health-units 50
```

### 4. Dados Mínimos para Testes
```bash
# O mínimo necessário para funcionar
uv run manage.py seed_all --users 5 --addresses 10 --health-units 2
```

## 🧪 Uso em Testes

### Pytest Fixtures
```python
# conftest.py
import pytest
from django.core.management import call_command

@pytest.fixture
def minimal_data():
    """Dados mínimos para testes básicos"""
    call_command('seed_addresses', '--count', '5')
    call_command('seed_health_units', '--count', '2')

@pytest.fixture
def full_accounts_data():
    """Dados completos do accounts para testes avançados"""
    call_command('seed_all', '--users', '10', '--addresses', '8')

@pytest.fixture
def health_catalogs():
    """Apenas catálogos de saúde"""
    call_command('seed_health_catalogs')
```

### Uso nos Testes
```python
def test_user_creation(minimal_data):
    # Teste com dados mínimos
    pass

def test_patient_workflow(full_accounts_data):
    # Teste com dados completos
    pass
```

## 🔧 Troubleshooting Rápido

### "Address matching query does not exist"
```bash
# Executar primeiro os endereços
uv run manage.py seed_addresses --count 10
```

### "No Health Units available"
```bash
# Executar na ordem correta
uv run manage.py seed_addresses --count 10
uv run manage.py seed_health_units --count 3
```

### Dados sempre iguais
```bash
# Normal! Para dados diferentes, altere o SECRET_KEY
export DJANGO_SECRET_KEY="nova-chave-para-dados-diferentes"
uv run manage.py seed_all
```

### Performance lenta
```bash
# Use quantidades menores
uv run manage.py seed_all --users 10 --addresses 15 --health-units 3
```

## 📊 Verificação Rápida de Dados

### Via Django Shell
```python
uv run manage.py shell
```

```python
# No shell
from accounts.models import User, Patient, Work, Session
from address.models import Address
from health_unit.models import HealthUnit
from profile_forms.models import ChronicDisease, Medicine, Allergy

# Contadores
print(f"📍 Endereços: {Address.objects.count()}")
print(f"🏥 Unidades de Saúde: {HealthUnit.objects.count()}")
print(f"👥 Usuários: {User.objects.count()}")
print(f"🏥 Pacientes: {Patient.objects.count()}")
print(f"💼 Trabalhos: {Work.objects.count()}")
print(f"⏰ Sessões: {Session.objects.count()}")
print(f"🏥 Doenças: {ChronicDisease.objects.count()}")
print(f"💊 Medicamentos: {Medicine.objects.count()}")
print(f"🤧 Alergias: {Allergy.objects.count()}")
```

### Via SQL Direto
```bash
uv run manage.py dbshell
```

```sql
-- No dbshell
SELECT 'Users' as table_name, COUNT(*) as count FROM accounts_user
UNION ALL
SELECT 'Patients', COUNT(*) FROM accounts_patient
UNION ALL
SELECT 'Addresses', COUNT(*) FROM address_address
UNION ALL
SELECT 'Health Units', COUNT(*) FROM health_unit_healthunit;
```

## 🛠️ Personalização Avançada

### Argumentos por Seed
```bash
# Endereços
uv run manage.py seed_addresses --count 100 --clear

# Unidades de Saúde
uv run manage.py seed_health_units --count 25 --clear

# Accounts
uv run manage.py seed_accounts --users 200 --patients 150 --works 100 --sessions 80 --clear

# Catálogos (sem argumentos personalizados)
uv run manage.py seed_health_catalogs --clear
```

### Combinações Úteis
```bash
# Reset completo com dados grandes
uv run manage.py seed_all --clear --users 100 --addresses 80 --health-units 20

# Apenas novos usuários (sem limpar existentes)
uv run manage.py seed_accounts --users 50

# Focar em dados médicos
uv run manage.py seed_all --skip seed_accounts --clear
```

## 🎯 Resumo dos Comandos Principais

| Comando | Uso | Exemplo |
|---------|-----|---------|
| `seed_all` | Tudo automaticamente | `python manage.py seed_all` |
| `seed_all --list` | Ver seeds disponíveis | `python manage.py seed_all --list` |
| `seed_all --only` | Seeds específicos | `python manage.py seed_all --only seed_addresses` |
| `seed_all --clear` | Limpar e recriar | `python manage.py seed_all --clear` |
| `seed_addresses` | Só endereços | `python manage.py seed_addresses --count 50` |
| `seed_accounts` | Só accounts | `python manage.py seed_accounts --users 100` |

## 💡 Dicas Finais

1. **Sempre execute `migrate` antes do seed**
2. **Use quantidades pequenas durante desenvolvimento**
3. **O seed é determinístico - mesma SECRET_KEY = mesmos dados**
4. **Seeds são seguros - não afetam superusuários**
5. **Use `--clear` com cuidado - remove dados existentes**
6. **Dependências são resolvidas automaticamente**
7. **Cada app gerencia seus próprios seeds**