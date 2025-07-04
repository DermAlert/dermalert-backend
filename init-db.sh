#!/bin/bash
# init-db.sh - Script para inicializar o banco de dados

echo "🔄 Aguardando PostgreSQL ficar disponível..."
while ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do
    sleep 1
done

echo "✅ PostgreSQL está disponível!"

echo "🔄 Executando migrações do Django..."
python manage.py migrate

echo "🔄 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "🔄 Criando superusuário se não existir..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        cpf='00000000000',
        email='admin@dermalert.com',
        password='admin123',
        first_name='Admin',
        last_name='DermAlert'
    )
    print("✅ Superusuário criado com sucesso!")
else:
    print("ℹ️  Superusuário já existe")
EOF

echo "✅ Inicialização do banco concluída!"
