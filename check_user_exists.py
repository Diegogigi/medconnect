#!/usr/bin/env python3
"""
Script para verificar si el usuario existe en Railway PostgreSQL
"""

import psycopg2
from psycopg2.extras import RealDictCursor


def check_user_exists():
    """Verifica si el usuario existe en la base de datos"""

    print("🔍 Verificando usuario en Railway PostgreSQL...")

    # Conectar a Railway PostgreSQL
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("✅ Conexión exitosa")

        # Verificar usuario específico
        email = "diego.castro.lagos@gmail.com"
        cursor.execute(
            """
            SELECT id, email, nombre, apellido, tipo_usuario, activo, password_hash
            FROM usuarios 
            WHERE email = %s;
        """,
            (email,),
        )

        user = cursor.fetchone()

        if user:
            print(f"\n👤 Usuario encontrado:")
            print(f"  - ID: {user['id']}")
            print(f"  - Email: {user['email']}")
            print(f"  - Nombre: {user['nombre']} {user['apellido']}")
            print(f"  - Tipo: {user['tipo_usuario']}")
            print(f"  - Activo: {user['activo']}")
            print(f"  - Password Hash: {user['password_hash'][:50]}...")
        else:
            print(f"\n❌ Usuario no encontrado: {email}")

            # Verificar todos los usuarios
            cursor.execute(
                """
                SELECT id, email, nombre, apellido, tipo_usuario, activo
                FROM usuarios 
                ORDER BY tipo_usuario, apellido, nombre;
            """
            )

            users = cursor.fetchall()
            print(f"\n👥 Todos los usuarios en la base de datos: {len(users)}")
            for u in users:
                status = "✅" if u["activo"] else "❌"
                print(
                    f"  {status} {u['nombre']} {u['apellido']} ({u['tipo_usuario']}) - {u['email']}"
                )

        cursor.close()
        conn.close()

        print(f"\n🎉 Verificación completada")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    check_user_exists()
