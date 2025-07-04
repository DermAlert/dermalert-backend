# Commands Reference

Este documento lista todos os comandos disponíveis para gerenciar seeds no DermAlert Backend.

## Comandos Make

### Seeds com Docker
- `make seed` - Executa todos os seeds
- `make seed-clear` - Limpa e recria todos os seeds
- `make seed-list` - Lista todos os seeds disponíveis
- `make seed-basic` - Executa seeds básicos (endereços e unidades de saúde)
- `make seed-minimal` - Executa seeds mínimos com dados limitados

### Seeds Locais
- `make seed-local` - Executa seeds localmente (sem Docker)
- `make seed-local-clear` - Limpa e recria seeds localmente
- `make seed-local-list` - Lista seeds disponíveis localmente
- `make seed-local-minimal` - Executa seeds mínimos localmente

### Utilitários
- `make seed-setup` - Configura ambiente para seeds
- `make seed-reset` - Reseta todos os dados
- `make seed-status` - Verifica status dos seeds

## Comandos Django Diretos

```bash
python manage.py seed_all
python manage.py seed_all --clear
python manage.py seed_all --list
python manage.py seed_all --only seed_addresses seed_health_units
```
