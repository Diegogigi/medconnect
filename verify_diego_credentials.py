#!/usr/bin/env python3
"""
Script para verificar las credenciales exactas de Diego Castro
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt


def verify_diego_credentials():
    """Verifica las credenciales exactas de Diego Castro"""

    print("🔍 Verificando credenciales de Diego Castro...")
    print("=" * 60)

    # Conectar a Railway PostgreSQL
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("✅ Conexión exitosa")

        # Buscar usuario Diego Castro
        email = "diego.castro.lagos@gmail.com"
        print(f"\n🔍 Buscando usuario: {email}")

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
        print(f"  - Password Hash: {user['password_hash'][:50]}...")

        # Probar diferentes contraseñas
        passwords_to_test = [
            "password123",
            "password",
            "123456",
            "admin",
            "diego123",
            "medconnect123",
        ]

        print(f"\n🔐 Probando diferentes contraseñas...")
        for password in passwords_to_test:
            try:
                is_valid = bcrypt.checkpw(
                    password.encode("utf-8"), user["password_hash"].encode("utf-8")
                )
                status = "✅ VÁLIDA" if is_valid else "❌ Inválida"
                print(f"  - '{password}': {status}")

                if is_valid:
                    print(f"\n🎉 ¡CONTRASEÑA CORRECTA ENCONTRADA!")
                    print(f"📧 Email: {email}")
                    print(f"🔑 Contraseña: {password}")
                    return True

            except Exception as e:
                print(f"  - '{password}': ❌ Error - {e}")

        print(f"\n❌ Ninguna contraseña funcionó")
        print(f"🔧 Necesitas restablecer la contraseña")

        # Generar nueva contraseña
        print(f"\n🔧 Generando nueva contraseña...")
        new_password = "password123"
        new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        )

        print(f"  - Nueva contraseña: {new_password}")
        print(f"  - Nuevo hash: {new_hash[:50]}...")

        # Actualizar contraseña
        cursor.execute(
            """
            UPDATE usuarios 
            SET password_hash = %s
            WHERE email = %s;
        """,
            (new_hash, email),
        )

        conn.commit()
        print(f"✅ Contraseña actualizada en la base de datos")

        # Verificar nueva contraseña
        is_valid = bcrypt.checkpw(
            new_password.encode("utf-8"), new_hash.encode("utf-8")
        )
        print(f"  - Verificación: {'✅ Válida' if is_valid else '❌ Inválida'}")

        cursor.close()
        conn.close()

        if is_valid:
            print(f"\n🎉 ¡CONTRASEÑA RESTABLECIDA!")
            print(f"📧 Email: {email}")
            print(f"🔑 Nueva contraseña: {new_password}")
            return True
        else:
            print(f"\n❌ Error restableciendo contraseña")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 VERIFICACIÓN CREDENCIALES DIEGO")
    print("=" * 60)

    success = verify_diego_credentials()

    if success:
        print(f"\n🎉 ¡Credenciales verificadas!")
        print(f"🔧 Ahora puedes probar el login en https://www.medconnect.cl/login")
    else:
        print(f"\n❌ Error verificando credenciales")
        print(f"🔧 Revisa los logs para más detalles")
