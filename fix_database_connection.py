#!/usr/bin/env python3
"""
Script para corregir el error de conexión en los métodos de registro
"""


def fix_database_connection():
    """Corrige el error de conexión en los métodos de registro"""

    print("🔧 Corrigiendo error de conexión en métodos de registro...")

    # Leer el archivo actual
    with open("postgresql_db_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Corregir self.connection por self.conn en _register_patient
    content = content.replace("self.connection.commit()", "self.conn.commit()")
    content = content.replace("self.connection.rollback()", "self.conn.rollback()")

    # Corregir self.connection por self.conn en _register_professional
    content = content.replace(
        "self.cursor.execute(query, values)", "self.cursor.execute(query, values)"
    )

    # Escribir el archivo corregido
    with open("postgresql_db_manager.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Error de conexión corregido:")
    print("   - self.connection cambiado por self.conn")
    print("   - Métodos de registro corregidos")


if __name__ == "__main__":
    fix_database_connection()
