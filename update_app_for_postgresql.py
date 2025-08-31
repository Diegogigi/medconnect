#!/usr/bin/env python3
"""
Script para actualizar la aplicación para usar PostgreSQL
"""

import os
import re


def update_app_for_postgresql():
    """Actualizar app.py para usar PostgreSQL"""

    print("🔧 Actualizando app.py para PostgreSQL...")

    # Leer el archivo actual
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Reemplazos necesarios
    replacements = [
        # Importar PostgreSQL en lugar de Google Sheets
        (
            'logger.info("[PAQUETE] Importando Google Sheets...")\n    import gspread\n    from google.oauth2.service_account import Credentials\n\n    logger.info("[OK] Google Sheets importado exitosamente")',
            'logger.info("[PAQUETE] Importando PostgreSQL...")\n    import psycopg2\n    from psycopg2.extras import RealDictCursor\n\n    logger.info("[OK] PostgreSQL importado exitosamente")',
        ),
        # Reemplazar SheetsManager con PostgreSQLManager
        (
            "from backend.database.sheets_manager import sheets_db",
            "from postgresql_db_manager import PostgreSQLDBManager",
        ),
        # Inicializar PostgreSQL en lugar de Google Sheets
        ("sheets_db = get_sheets_manager()", "postgres_db = PostgreSQLDBManager()"),
        # Actualizar referencias de sheets_db a postgres_db
        ("sheets_db.get_all_records_fallback", "postgres_db.get_all_records"),
        # Agregar configuración de PostgreSQL
        (
            'logger.info("[OK] Todas las importaciones completadas exitosamente")',
            """logger.info("[OK] Todas las importaciones completadas exitosamente")

# Configurar PostgreSQL
logger.info("[CONFIG] Configurando PostgreSQL...")
try:
    postgres_db = PostgreSQLDBManager()
    if postgres_db.is_connected():
        logger.info("[OK] PostgreSQL configurado exitosamente")
    else:
        logger.error("[ERROR] No se pudo conectar a PostgreSQL")
        postgres_db = None
except Exception as e:
    logger.error(f"[ERROR] Error configurando PostgreSQL: {e}")
    postgres_db = None""",
        ),
    ]

    # Aplicar reemplazos
    for old_text, new_text in replacements:
        content = content.replace(old_text, new_text)

    # Escribir el archivo actualizado
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ app.py actualizado para PostgreSQL")


def update_auth_manager():
    """Actualizar auth_manager.py para usar PostgreSQL"""

    print("🔧 Actualizando auth_manager.py para PostgreSQL...")

    # Leer el archivo actual
    with open("auth_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Reemplazos necesarios
    replacements = [
        # Importar PostgreSQL
        (
            "import gspread\nfrom google.oauth2.service_account import Credentials",
            "import psycopg2\nfrom psycopg2.extras import RealDictCursor",
        ),
        # Actualizar método de autenticación
        (
            "def authenticate_user(self, email, password):",
            """def authenticate_user(self, email, password):
        \"\"\"Autenticar usuario usando PostgreSQL\"\"\"
        try:
            if not hasattr(self, 'postgres_db'):
                from postgresql_db_manager import PostgreSQLDBManager
                self.postgres_db = PostgreSQLDBManager()
            
            if not self.postgres_db.is_connected():
                logger.error("❌ No se pudo conectar a PostgreSQL")
                return None
            
            # Buscar usuario en PostgreSQL
            user = self.postgres_db.get_user_by_email(email)
            if user and self.verify_password(password, user['password_hash']):
                return user
            return None
        except Exception as e:
            logger.error(f"❌ Error en autenticación: {e}")
            return None""",
        ),
    ]

    # Aplicar reemplazos
    for old_text, new_text in replacements:
        content = content.replace(old_text, new_text)

    # Escribir el archivo actualizado
    with open("auth_manager.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ auth_manager.py actualizado para PostgreSQL")


def create_postgresql_config():
    """Crear archivo de configuración para PostgreSQL"""

    config_content = '''#!/usr/bin/env python3
"""
Configuración para PostgreSQL
"""

import os

def get_postgresql_config():
    """Obtener configuración de PostgreSQL"""
    return {
        'host': os.environ.get('PGHOST', 'localhost'),
        'port': os.environ.get('PGPORT', '5432'),
        'database': os.environ.get('PGDATABASE', 'railway'),
        'user': os.environ.get('PGUSER', 'postgres'),
        'password': os.environ.get('PGPASSWORD', ''),
        'database_url': os.environ.get('DATABASE_URL')
    }

def get_config():
    """Obtener configuración general"""
    return {
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key'),
        'FLASK_ENV': os.environ.get('FLASK_ENV', 'development'),
        'PORT': int(os.environ.get('PORT', 5000)),
        'OPENROUTER_API_KEY': os.environ.get('OPENROUTER_API_KEY'),
        'postgresql': get_postgresql_config()
    }
'''

    with open("postgresql_config.py", "w", encoding="utf-8") as f:
        f.write(config_content)

    print("✅ postgresql_config.py creado")


if __name__ == "__main__":
    print("🚀 Actualizando aplicación para PostgreSQL...")

    try:
        update_app_for_postgresql()
        update_auth_manager()
        create_postgresql_config()

        print("\n🎉 ¡Aplicación actualizada para PostgreSQL!")
        print("📋 Cambios realizados:")
        print("  ✅ app.py - Actualizado para usar PostgreSQL")
        print("  ✅ auth_manager.py - Actualizado para PostgreSQL")
        print("  ✅ postgresql_config.py - Creado")
        print("\n💡 Próximo paso: Hacer commit y push de los cambios")

    except Exception as e:
        print(f"❌ Error actualizando aplicación: {e}")
