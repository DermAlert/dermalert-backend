# API - Health Units

Documentação da API de unidades de saúde do DermAlert Backend.

## Endpoints

### Unidades de Saúde

#### GET /api/health-units/
Lista todas as unidades de saúde

#### POST /api/health-units/
Cria uma nova unidade de saúde

#### GET /api/health-units/{id}/
Obtém detalhes de uma unidade específica

#### PUT /api/health-units/{id}/
Atualiza uma unidade existente

#### DELETE /api/health-units/{id}/
Remove uma unidade de saúde

## Modelos

### HealthUnit
- id: UUID
- name: CharField
- description: TextField
- address: ForeignKey(Address)
- phone: CharField
- email: EmailField
- is_active: BooleanField
- created_at: DateTimeField

## Filtros Disponíveis

- Por nome
- Por cidade
- Por estado
- Por status (ativo/inativo)

## Permissões

- Leitura: Usuários autenticados
- Escrita: Administradores e gestores de saúde
