# Configuração PostgreSQL - DermAlert Backend

Este documento explica como configurar e usar PostgreSQL em desenvolvimento e produção.

## 🚀 Início Rápido

### Desenvolvimento

1. **Instalar dependências:**
   ```bash
   uv sync --group dev
   ```

2. **Subir os serviços (PostgreSQL + MinIO + Django):**
   ```bash
   make dev
   ```

3. **Executar migrações (em outro terminal):**
   ```bash
   make setup-db
   ```

### Produção

1. **Configurar variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Editar .env com suas configurações de produção
   ```

2. **Subir os serviços:**
   ```bash
   make prod
   ```

## 📦 Serviços

### Desenvolvimento (`docker-compose.dev.yml`)
- **PostgreSQL**: `localhost:5432`
- **MinIO**: `localhost:9000` (Console: `localhost:9090`)
- **Django**: `localhost:8000`

### Produção (`docker-compose.yml`)
- **PostgreSQL**: Interno (porta 5432)
- **MinIO**: Interno (porta 9000)
- **Django**: Através do Nginx (porta 80/443)
- **Nginx**: `localhost:80` e `localhost:443`

## 🗄️ Banco de Dados

### Configuração Automática

O projeto detecta automaticamente se deve usar PostgreSQL ou SQLite:
- **PostgreSQL**: Se `POSTGRES_DB` estiver definido no `.env`
- **SQLite**: Fallback se PostgreSQL não estiver configurado

### Variáveis de Ambiente

```bash
# PostgreSQL
POSTGRES_DB=django_db
POSTGRES_USER=django_user
POSTGRES_PASSWORD=sua_senha_forte
POSTGRES_HOST=postgres  # Nome do serviço no Docker
POSTGRES_PORT=5432
```

### Comandos Úteis

```bash
# Conectar ao banco via psql
make db-shell

# Executar migrações
make migrate

# Shell do Django
make shell

# Ver logs do PostgreSQL
docker compose -f docker-compose.dev.yml logs postgres

# Backup do banco
docker compose -f docker-compose.dev.yml exec postgres pg_dump -U django_user django_db > backup.sql

# Restaurar backup
docker compose -f docker-compose.dev.yml exec -T postgres psql -U django_user django_db < backup.sql
```

## 🔒 Segurança

### Desenvolvimento
- Usar senhas padrão (já configuradas)
- PostgreSQL exposto na porta 5432

### Produção
- **SEMPRE** alterar senhas padrão
- PostgreSQL não exposto externamente
- Configurar HTTPS no Nginx
- Usar senhas fortes e únicas

### Exemplo de senhas fortes:
```bash
# Gerar senha aleatória
openssl rand -base64 32
```

## 🔧 Troubleshooting

### PostgreSQL não conecta
```bash
# Verificar se o serviço está rodando
docker compose -f docker-compose.dev.yml ps

# Ver logs do PostgreSQL
docker compose -f docker-compose.dev.yml logs postgres

# Reiniciar apenas o PostgreSQL
docker compose -f docker-compose.dev.yml restart postgres
```

### Erro de migração
```bash
# Resetar migrações (CUIDADO: apaga dados!)
docker compose -f docker-compose.dev.yml exec postgres psql -U django_user -c "DROP DATABASE django_db;"
docker compose -f docker-compose.dev.yml exec postgres psql -U django_user -c "CREATE DATABASE django_db;"
make migrate
```

### Performance
```bash
# Verificar conexões ativas
docker compose -f docker-compose.dev.yml exec postgres psql -U django_user django_db -c "SELECT * FROM pg_stat_activity;"

# Verificar tamanho do banco
docker compose -f docker-compose.dev.yml exec postgres psql -U django_user django_db -c "SELECT pg_size_pretty(pg_database_size('django_db'));"
```

## 🌐 URLs Importantes

- **Django Admin**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/
- **MinIO Console**: http://localhost:9090/
- **PostgreSQL**: `localhost:5432` (apenas desenvolvimento)

## 📚 Próximos Passos

1. Configure backup automático para produção
2. Implemente monitoramento com logs
3. Configure SSL/TLS para HTTPS
4. Considere usar Connection Pooling (PgBouncer)
5. Configure replicação para alta disponibilidade
