#!/usr/bin/env python3
"""
Script para eliminar la doble instancia de DB
"""


def fix_double_db_instance():
    """Elimina la doble instancia de DB"""

    print("🔧 Eliminando doble instancia de DB...")

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar la inicialización duplicada
    old_init = """# Dependencias opcionales que tu app menciona:
auth_manager = None
postgres_db = None

# Inicializar PostgreSQL una sola vez
try:
    from postgresql_db_manager import PostgreSQLDBManager
    postgres_db = PostgreSQLDBManager()
    print(f"[INFO] PostgreSQLDBManager inicializado: {'Conectado' if postgres_db.is_connected() else 'Modo fallback'}")
except Exception as e:
    print(f"[WARN] PostgreSQLDBManager no disponible: {e}")

# Inicializar AuthManager con la instancia de PostgreSQL
try:
    from auth_manager import AuthManager
    auth_manager = AuthManager(postgres_db=postgres_db)  # Pasar la instancia existente
except Exception as e:
    print(f"[WARN] AuthManager no disponible: {e}")"""

    new_init = """# Dependencias opcionales que tu app menciona:
auth_manager = None
postgres_db = None

# Inicializar PostgreSQL una sola vez
try:
    from postgresql_db_manager import PostgreSQLDBManager
    postgres_db = PostgreSQLDBManager()
    logger.info(f"✅ PostgreSQLDBManager inicializado: {'Conectado' if postgres_db.is_connected() else 'Modo fallback'}")
except Exception as e:
    logger.warning(f"⚠️ PostgreSQLDBManager no disponible: {e}")

# Inicializar AuthManager con la instancia de PostgreSQL
try:
    from auth_manager import AuthManager
    auth_manager = AuthManager(db_instance=postgres_db)  # Pasar la instancia existente
except Exception as e:
    logger.warning(f"⚠️ AuthManager no disponible: {e}")"""

    # Reemplazar en el contenido
    if old_init in content:
        content = content.replace(old_init, new_init)

        # Escribir el archivo actualizado
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Doble instancia de DB eliminada")
        print("🔧 Ahora solo hay una instancia de PostgreSQLDBManager")
    else:
        print("❌ No se encontró la inicialización duplicada")


if __name__ == "__main__":
    fix_double_db_instance()
