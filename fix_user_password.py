#!/usr/bin/env python3
"""
Script para corregir la contraseña del usuario en Railway PostgreSQL
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt


def fix_user_password():
    """Corrige la contraseña del usuario en la base de datos"""

    print("🔧 Corrigiendo contraseña del usuario...")
    print("=" * 60)

    # Conectar a Railway PostgreSQL
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("✅ Conexión exitosa")

        # Usuario a corregir
        email = "diego.castro.lagos@gmail.com"
        new_password = "password123"

        print(f"\n🔍 Buscando usuario: {email}")

        # Buscar usuario
        cursor.execute(
            """
            SELECT id, email, nombre, apellido, tipo_usuario, activo
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

        # Generar nuevo hash de contraseña
        print(f"\n🔐 Generando nuevo hash de contraseña...")
        password_hash = bcrypt.hashpw(
            new_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        print(f"  - Nueva contraseña: {new_password}")
        print(f"  - Nuevo hash: {password_hash[:50]}...")

        # Actualizar contraseña en la base de datos
        print(f"\n💾 Actualizando contraseña en la base de datos...")
        cursor.execute(
            """
            UPDATE usuarios 
            SET password_hash = %s
            WHERE email = %s;
        """,
            (password_hash, email),
        )

        # Confirmar cambios
        conn.commit()
        print(f"✅ Contraseña actualizada exitosamente")

        # Verificar que funciona
        print(f"\n🧪 Verificando nueva contraseña...")
        cursor.execute(
            """
            SELECT password_hash
            FROM usuarios 
            WHERE email = %s;
        """,
            (email,),
        )

        result = cursor.fetchone()
        if result:
            stored_hash = result["password_hash"]
            is_valid = bcrypt.checkpw(
                new_password.encode("utf-8"), stored_hash.encode("utf-8")
            )
            print(f"  - Verificación: {'✅ Válida' if is_valid else '❌ Inválida'}")

            if is_valid:
                print(f"✅ Contraseña corregida exitosamente")
                return True
            else:
                print(f"❌ Error en la verificación")
                return False
        else:
            print(f"❌ No se pudo verificar la contraseña")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if "conn" in locals():
            conn.close()


def fix_second_user():
    """Corrige la contraseña del segundo usuario"""

    print(f"\n🔧 Corrigiendo segundo usuario...")

    # Conectar a Railway PostgreSQL
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Segundo usuario
        email = "rodrigoandressilvabreve@gmail.com"
        new_password = "password123"

        print(f"🔍 Buscando usuario: {email}")

        # Buscar usuario
        cursor.execute(
            """
            SELECT id, email, nombre, apellido, tipo_usuario, activo
            FROM usuarios 
            WHERE email = %s;
        """,
            (email,),
        )

        user = cursor.fetchone()

        if not user:
            print(f"❌ Usuario no encontrado: {email}")
            return False

        print(f"✅ Usuario encontrado: {user['nombre']} {user['apellido']}")

        # Generar nuevo hash de contraseña
        password_hash = bcrypt.hashpw(
            new_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Actualizar contraseña
        cursor.execute(
            """
            UPDATE usuarios 
            SET password_hash = %s
            WHERE email = %s;
        """,
            (password_hash, email),
        )

        conn.commit()
        print(f"✅ Contraseña del segundo usuario actualizada")

        return True

    except Exception as e:
        print(f"❌ Error actualizando segundo usuario: {e}")
        return False
    finally:
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    print("🚀 CORRECCIÓN CONTRASEÑAS USUARIOS")
    print("=" * 60)

    success1 = fix_user_password()
    success2 = fix_second_user()

    if success1 and success2:
        print(f"\n🎉 ¡Contraseñas corregidas exitosamente!")
        print(f"🔧 Ahora puedes probar el login en https://www.medconnect.cl/login")
        print(f"📧 Credenciales:")
        print(f"   - diego.castro.lagos@gmail.com / password123")
        print(f"   - rodrigoandressilvabreve@gmail.com / password123")
    else:
        print(f"\n❌ Error corrigiendo contraseñas")
        print(f"🔧 Revisa los logs para más detalles")
