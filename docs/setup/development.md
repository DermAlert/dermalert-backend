# Ambiente de Desenvolvimento

Este documento descreve como configurar o ambiente de desenvolvimento para o DermAlert Backend.

## Pré-requisitos

- Docker e Docker Compose
- Python 3.13+
- uv (Python package manager)

## Configuração

1. Clone o repositório
2. Execute `make dev` para iniciar o ambiente de desenvolvimento
3. Execute `make setup-db` para configurar o banco de dados

## Comandos Úteis

- `make dev` - Inicia o ambiente de desenvolvimento
- `make test` - Executa os testes
- `make lint` - Executa o linter
- `make docs` - Inicia o servidor de documentação
