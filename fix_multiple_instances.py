#!/usr/bin/env python3
"""
Script para arreglar múltiples instancias de PostgreSQL
"""


def fix_multiple_instances():
    """Arregla las múltiples instancias de PostgreSQL"""

    print("🔧 Arreglando múltiples instancias de PostgreSQL...")

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar la inicialización problemática
    old_init = """# Dependencias opcionales que tu app menciona:
auth_manager = None
postgres_db = None
try:
    from auth_manager import AuthManager

    auth_manager = AuthManager()
except Exception as e:
    print(f"[WARN] AuthManager no disponible: {e}")

try:
    from postgresql_db_manager import PostgreSQLDBManager

    postgres_db = PostgreSQLDBManager()
except Exception as e:
    print(f"[WARN] PostgreSQLDBManager no disponible: {e}")"""

    new_init = """# Dependencias opcionales que tu app menciona:
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
    auth_manager = AuthManager(db_instance=postgres_db)  # Pasar la instancia existente
    print(f"[INFO] AuthManager inicializado correctamente")
except Exception as e:
    print(f"[WARN] AuthManager no disponible: {e}")"""

    # Reemplazar en el contenido
    if old_init in content:
        content = content.replace(old_init, new_init)

        # También necesitamos arreglar la línea donde se vuelve a crear AuthManager
        old_auth_line = "auth_manager = AuthManager()"
        new_auth_line = "# auth_manager ya inicializado arriba"

        content = content.replace(old_auth_line, new_auth_line)

        # Escribir el archivo actualizado
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Múltiples instancias arregladas")
        print("🔧 Ahora solo habrá una instancia de PostgreSQL por worker")
        print("🔧 AuthManager usará la misma instancia de PostgreSQL")
    else:
        print("❌ No se encontró la inicialización problemática")


if __name__ == "__main__":
    fix_multiple_instances()
