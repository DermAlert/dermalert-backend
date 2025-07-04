# Arquitetura

Este documento descreve a arquitetura do DermAlert Backend.

## Visão Geral

O DermAlert Backend é uma aplicação Django REST Framework que fornece APIs para um sistema de diagnóstico dermatológico com IA.

## Componentes Principais

### Apps Django

1. **accounts** - Gerenciamento de usuários e autenticação
2. **address** - Gerenciamento de endereços
3. **health_unit** - Gerenciamento de unidades de saúde
4. **consultations** - Gerenciamento de consultas
5. **ml** - Integração com modelos de machine learning
6. **skin_conditions** - Condições dermatológicas
7. **skin_forms** - Formulários de avaliação
8. **profile_forms** - Formulários de perfil

### Banco de Dados

- **PostgreSQL** - Banco principal
- **Redis** (planejado) - Cache e filas

### Infraestrutura

- **Docker** - Containerização
- **nginx** - Proxy reverso
- **Gunicorn** - Servidor WSGI

## Padrões Arquiteturais

### DRF (Django REST Framework)
- ViewSets para endpoints CRUD
- Serializers para validação e transformação
- Permissions para controle de acesso

### Estrutura de Apps
```
app/
├── models/
├── serializers/
├── views/
├── tests/
├── migrations/
└── management/commands/
```

## Integração com IA

O módulo `ml` gerencia:
- Processamento de imagens
- Comunicação com modelos de IA
- Armazenamento de resultados
