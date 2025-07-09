# Configuração MinIO - DermAlert Backend

Este documento explica como configurar e usar o MinIO (S3-compatible) para armazenamento de arquivos no projeto DermAlert.

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

3. **Configurar MinIO (em outro terminal):**
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
- **MinIO**: `localhost:9000` (Console: `localhost:9090`)
- **PostgreSQL**: `localhost:5432`
- **Django**: `localhost:8000`

### Produção (`docker-compose.yml`)
- **MinIO**: Interno (porta 9000)
- **PostgreSQL**: Interno (porta 5432)
- **Django**: Através do Nginx (porta 80/443)
- **Nginx**: `localhost:80` e `localhost:443`

## 🗄️ Armazenamento de Objetos

### Configuração Automática

O projeto usa MinIO como alternativa local ao Amazon S3:
- **MinIO**: Para desenvolvimento e produção local
- **S3**: Para produção em nuvem (configuração opcional)

### Variáveis de Ambiente

```bash
# MinIO Configuration
USE_S3=True
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_STORAGE_BUCKET_NAME=dermalert
AWS_S3_CUSTOM_DOMAIN=localhost:9000
AWS_S3_ENDPOINT_URL=http://minio:9000
AWS_S3_REGION_NAME=us-east-1
AWS_S3_URL_PROTOCOL=http:
```

### Comandos Úteis

```bash
# Configurar MinIO automaticamente
make setup-db

# Configurar MinIO manualmente
docker compose -f docker-compose.dev.yml exec dermalert uv run manage.py setup_minio

# Configurar MinIO com teste de upload
docker compose -f docker-compose.dev.yml exec dermalert uv run manage.py setup_minio --test-upload

# Apenas criar bucket (sem política)
docker compose -f docker-compose.dev.yml exec dermalert uv run manage.py setup_minio --skip-policy

# Ver logs do MinIO
docker compose -f docker-compose.dev.yml logs minio

# Acessar MinIO Console
# Abrir http://localhost:9090 no navegador
# Usuário: minioadmin / Senha: minioadmin
```

## 🔧 Comando `setup_minio`

O comando personalizado `setup_minio` configura automaticamente o MinIO:

### Funcionalidades

1. **Verifica/Cria o bucket** configurado em `AWS_STORAGE_BUCKET_NAME`
2. **Aplica bucket-policy** para leitura anônima em `static/*`
3. **Testa upload** (opcional) para validar configuração

### Uso

```bash
# Configuração completa
uv run manage.py setup_minio

# Pular configuração de política
uv run manage.py setup_minio --skip-policy

# Incluir teste de upload
uv run manage.py setup_minio --test-upload

# Combinado
uv run manage.py setup_minio --test-upload --skip-policy
```

### Saída do Comando

```
Bucket alvo: dermalert
‣ Verificando bucket… OK
‣ Aplicando bucket-policy em static/*… OK
‣ Enviando arquivo de teste… OK
```

## 🏗️ Estrutura do Bucket

```
dermalert/
├── static/                 # Arquivos estáticos (CSS, JS, imagens)
│   ├── admin/
│   ├── rest_framework/
│   └── ...
├── media/                  # Uploads de usuários
│   ├── profile_images/
│   ├── skin_images/
│   └── consent_forms/
└── test/                   # Arquivos de teste
    └── test_file.txt
```

## 🔒 Segurança

### Desenvolvimento
- Usar credenciais padrão (`minioadmin`/`minioadmin`)
- MinIO exposto nas portas 9000 e 9090
- Política de leitura anônima em `static/*`

### Produção
- **SEMPRE** alterar credenciais padrão
- MinIO não exposto externamente
- Configurar HTTPS no Nginx
- Usar senhas fortes e únicas

### Exemplo de senhas fortes:
```bash
# Gerar senha aleatória
openssl rand -base64 32

# Ou usar uuidgen
uuidgen | tr '[:upper:]' '[:lower:]' | tr -d '-'
```

## 📋 Políticas de Bucket

### Política Padrão (static/*)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"AWS": ["*"]},
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::dermalert/static/*"]
    }
  ]
}
```

### Configuração Personalizada

```python
# Em core/minio_utils.py
def set_static_prefix_read_only(bucket=None, prefix="static/*"):
    """Configura leitura anônima para um prefixo específico"""
    # Implementação automática
```

## 🔧 Troubleshooting

### MinIO não conecta
```bash
# Verificar se o serviço está rodando
docker compose -f docker-compose.dev.yml ps

# Ver logs do MinIO
docker compose -f docker-compose.dev.yml logs minio

# Reiniciar apenas o MinIO
docker compose -f docker-compose.dev.yml restart minio
```

### Erro de permissão
```bash
# Reconfigurar bucket e políticas
docker compose -f docker-compose.dev.yml exec dermalert uv run manage.py setup_minio

# Verificar configuração no MinIO Console
# http://localhost:9090/buckets/dermalert/admin/summary
```

### Bucket não encontrado
```bash
# Recriar bucket
docker compose -f docker-compose.dev.yml exec dermalert uv run manage.py setup_minio

# Verificar configuração
docker compose -f docker-compose.dev.yml exec dermalert uv run manage.py shell
```

```python
# No Django shell
from django.conf import settings
from core.minio_utils import bucket_exists, create_bucket_if_not_exists

print(f"Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
print(f"Endpoint: {settings.AWS_S3_ENDPOINT_URL}")
print(f"Existe: {bucket_exists(settings.AWS_STORAGE_BUCKET_NAME)}")
```

### Performance lenta
```bash
# Verificar saúde do MinIO
docker compose -f docker-compose.dev.yml exec minio curl -f http://localhost:9000/minio/health/live

# Verificar espaço em disco
docker compose -f docker-compose.dev.yml exec minio df -h /data
```

## 🔄 Migração de Dados

### Backup de Bucket

```bash
# Exportar dados do MinIO
docker compose -f docker-compose.dev.yml exec minio mc mirror /data/dermalert /backup/dermalert

# Ou usar mc client
docker run --rm -it --network dermalert_default \
  -v $(pwd)/backup:/backup \
  minio/mc:latest \
  mirror minio/dermalert /backup/dermalert
```

### Restaurar Backup

```bash
# Importar dados para MinIO
docker compose -f docker-compose.dev.yml exec minio mc mirror /backup/dermalert /data/dermalert
```

## 🌐 URLs Importantes

- **MinIO Console**: http://localhost:9090/
- **Django Admin**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/
- **PostgreSQL**: `localhost:5432` (apenas desenvolvimento)

## 🛠️ Integração com Django

### Configuração em `settings.py`

```python
# Configuração S3/MinIO
AWS_ACCESS_KEY_ID       = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
AWS_SECRET_ACCESS_KEY   = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
AWS_S3_ENDPOINT_URL     = os.getenv("AWS_S3_ENDPOINT_URL", "http://minio:9000")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "dermalert")
AWS_S3_REGION_NAME      = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
AWS_S3_CUSTOM_DOMAIN    = os.getenv("AWS_S3_CUSTOM_DOMAIN", "localhost:9000")
AWS_QUERYSTRING_AUTH    = False
AWS_DEFAULT_ACL         = "public-read"

STATIC_URL = f"{AWS_STORAGE_BUCKET_NAME}/static/"
```

### Utilitários Disponíveis

```python
from core.minio_utils import (
    create_minio_client,
    bucket_exists,
    create_bucket_if_not_exists,
    set_static_prefix_read_only,
    upload_test_file,
)

# Criar cliente
client = create_minio_client()

# Verificar bucket
if bucket_exists("meu-bucket"):
    print("Bucket existe!")

# Criar bucket
create_bucket_if_not_exists("novo-bucket")

# Configurar política
set_static_prefix_read_only("meu-bucket", "public/*")

# Testar upload
if upload_test_file():
    print("Upload funcionando!")
```

## 📚 Próximos Passos

1. Configure backup automático para produção
2. Implemente monitoramento de uso de armazenamento
3. Configure CDN para melhor performance
4. Considere usar S3 oficial para produção em nuvem
5. Configure lifecycle policies para arquivos antigos

## 🎯 Casos de Uso

### Upload de Arquivos

```python
# models.py
from django.db import models

class SkinImage(models.Model):
    image = models.ImageField(upload_to='skin_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_image_url(self):
        return f"http://localhost:9000/{settings.AWS_STORAGE_BUCKET_NAME}/{self.image.name}"
```

### Servir Arquivos Estáticos

```python
# settings.py
STATIC_URL = f"http://localhost:9000/{AWS_STORAGE_BUCKET_NAME}/static/"
MEDIA_URL = f"http://localhost:9000/{AWS_STORAGE_BUCKET_NAME}/media/"
```

### Validação de Configuração

```python
# views.py
from django.http import JsonResponse
from core.minio_utils import bucket_exists

def minio_status(request):
    try:
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        return JsonResponse({
            'status': 'ok',
            'bucket': bucket_name,
            'exists': bucket_exists(bucket_name),
            'endpoint': settings.AWS_S3_ENDPOINT_URL
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })
```
