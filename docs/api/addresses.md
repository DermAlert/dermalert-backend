# API - Endereços

Documentação da API de endereços do DermAlert Backend.

## Endpoints

### Endereços

#### GET /api/addresses/
Lista todos os endereços

#### POST /api/addresses/
Cria um novo endereço

#### GET /api/addresses/{id}/
Obtém detalhes de um endereço específico

#### PUT /api/addresses/{id}/
Atualiza um endereço existente

#### DELETE /api/addresses/{id}/
Remove um endereço

## Modelos

### Address
- id: UUID
- street: CharField
- number: CharField
- complement: CharField (opcional)
- neighborhood: CharField
- city: CharField
- state: CharField
- postal_code: CharField
- country: CharField
- latitude: DecimalField (opcional)
- longitude: DecimalField (opcional)

## Filtros Disponíveis

- Por cidade
- Por estado
- Por CEP
- Por bairro

## Validações

- CEP deve seguir formato brasileiro (XXXXX-XXX)
- Estado deve ser uma sigla válida
- Coordenadas geográficas devem estar em formato decimal

## Permissões

- Leitura: Usuários autenticados
- Escrita: Administradores e usuários proprietários
