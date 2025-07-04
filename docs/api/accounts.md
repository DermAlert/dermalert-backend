# API - Accounts

Documentação da API de contas de usuário do DermAlert Backend.

## Endpoints

### Usuários

#### GET /api/accounts/users/
Lista todos os usuários

#### POST /api/accounts/users/
Cria um novo usuário

#### GET /api/accounts/users/{id}/
Obtém detalhes de um usuário específico

#### PUT /api/accounts/users/{id}/
Atualiza um usuário existente

#### DELETE /api/accounts/users/{id}/
Remove um usuário

### Autenticação

#### POST /api/accounts/auth/login/
Realiza login do usuário

#### POST /api/accounts/auth/logout/
Realiza logout do usuário

#### POST /api/accounts/auth/register/
Registra um novo usuário

## Modelos

### User
- id: UUID
- email: EmailField
- first_name: CharField
- last_name: CharField
- is_active: BooleanField
- date_joined: DateTimeField

## Permissões

- Usuários autenticados podem visualizar próprio perfil
- Administradores podem gerenciar todos os usuários
