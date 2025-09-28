#!/usr/bin/env python3
"""
Script para probar el login directamente con la base de datos
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt


def test_login_direct():
    """Prueba el login directamente con la base de datos"""

    print("🔐 Probando login directamente con la base de datos...")
    print("=" * 60)

    # Conectar a Railway PostgreSQL
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("✅ Conexión exitosa")

        # Credenciales de prueba
        email = "diego.castro.lagos@gmail.com"
        password = "password123"

        print(f"\n🔍 Buscando usuario: {email}")

        # Buscar usuario
        cursor.execute(
            """
            SELECT id, email, nombre, apellido, tipo_usuario, activo, password_hash
            FROM usuarios 
            WHERE email = %s;
        """,
            (email,),
        )

        user = cursor.fetchone()

        if not user:
            print(f"❌ Usuario no encontrado: {email}")
            return False

        print(f"✅ Usuario encontrado:")
        print(f"  - ID: {user['id']}")
        print(f"  - Email: {user['email']}")
        print(f"  - Nombre: {user['nombre']} {user['apellido']}")
        print(f"  - Tipo: {user['tipo_usuario']}")
        print(f"  - Activo: {user['activo']}")

        if not user["activo"]:
            print(f"❌ Usuario inactivo")
            return False

        # Verificar contraseña
        print(f"\n🔐 Verificando contraseña...")
        stored_hash = user["password_hash"]
        print(f"  - Hash almacenado: {stored_hash[:50]}...")

        # Probar con bcrypt
        try:
            password_bytes = password.encode("utf-8")
            hash_bytes = stored_hash.encode("utf-8")

            is_valid = bcrypt.checkpw(password_bytes, hash_bytes)
            print(
                f"  - Verificación bcrypt: {'✅ Válida' if is_valid else '❌ Inválida'}"
            )

            if is_valid:
                print(f"✅ Login exitoso con la base de datos")
                return True
            else:
                print(f"❌ Contraseña incorrecta")

                # Probar con contraseña alternativa
                alt_password = "password"
                alt_is_valid = bcrypt.checkpw(alt_password.encode("utf-8"), hash_bytes)
                print(
                    f"  - Prueba con 'password': {'✅ Válida' if alt_is_valid else '❌ Inválida'}"
                )

                return False

        except Exception as e:
            print(f"❌ Error verificando contraseña: {e}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if "conn" in locals():
            conn.close()


def test_password_hash():
    """Prueba crear un hash de contraseña"""

    print(f"\n🔧 Probando creación de hash de contraseña...")

    password = "password123"
    hash_result = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

    print(f"  - Contraseña: {password}")
    print(f"  - Hash generado: {hash_result[:50]}...")

    # Verificar que funciona
    is_valid = bcrypt.checkpw(password.encode("utf-8"), hash_result.encode("utf-8"))
    print(f"  - Verificación: {'✅ Válida' if is_valid else '❌ Inválida'}")


if __name__ == "__main__":
    print("🚀 PRUEBA LOGIN DIRECTO")
    print("=" * 60)

    success = test_login_direct()
    test_password_hash()

    if success:
        print(f"\n🎉 ¡Login directo exitoso!")
        print(f"🔧 El problema puede estar en la aplicación web")
    else:
        print(f"\n❌ Login directo fallido")
        print(f"🔧 Revisa las credenciales o la base de datos")
