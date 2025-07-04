#!/usr/bin/env python3
"""
Script para testar a conexão com PostgreSQL
Usage: python check_db.py
"""
import os
import sys
import psycopg2
from pathlib import Path

# Adicionar o projeto ao Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dermalert.settings')

try:
    import django
    django.setup()
    
    from django.db import connection
    from django.core.management.color import color_style
    
    style = color_style()
    
    print(style.HTTP_SUCCESS("🔍 Testando conexão com o banco de dados..."))
    
    # Testar conexão
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
    if result:
        print(style.HTTP_SUCCESS("✅ Conexão com PostgreSQL estabelecida com sucesso!"))
        
        # Informações do banco
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"📊 Versão do PostgreSQL: {version}")
            
            cursor.execute("SELECT current_database();")
            database = cursor.fetchone()[0]
            print(f"🗄️  Database atual: {database}")
            
            cursor.execute("SELECT current_user;")
            user = cursor.fetchone()[0]
            print(f"👤 Usuário atual: {user}")
            
            # Listar tabelas
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            if tables:
                print(f"📋 Tabelas encontradas ({len(tables)}):")
                for table in tables[:10]:  # Mostrar apenas as primeiras 10
                    print(f"   - {table[0]}")
                if len(tables) > 10:
                    print(f"   ... e mais {len(tables) - 10} tabelas")
            else:
                print("📋 Nenhuma tabela encontrada. Execute 'python manage.py migrate' primeiro.")
                
    else:
        print(style.ERROR("❌ Falha na conexão com PostgreSQL"))
        sys.exit(1)
        
except Exception as e:
    print(style.ERROR(f"❌ Erro ao conectar com o banco: {e}"))
    print(style.WARNING("💡 Dicas para resolver:"))
    print("   1. Verifique se o PostgreSQL está rodando: docker compose ps")
    print("   2. Verifique as variáveis de ambiente no .env")
    print("   3. Verifique se as credenciais estão corretas")
    sys.exit(1)
