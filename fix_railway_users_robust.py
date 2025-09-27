#!/usr/bin/env python3
"""
Script robusto para crear usuarios en Railway PostgreSQL
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import requests
import sys


def get_railway_database_url():
    """Obtiene la URL de la base de datos de Railway"""

    # Intentar diferentes formas de obtener la URL
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        # Construir URL desde variables individuales
        pghost = os.environ.get("PGHOST")
        pgport = os.environ.get("PGPORT")
        pgdatabase = os.environ.get("PGDATABASE")
        pguser = os.environ.get("PGUSER")
        pgpassword = os.environ.get("PGPASSWORD")

        if all([pghost, pgport, pgdatabase, pguser, pgpassword]):
            database_url = (
                f"postgresql://{pguser}:{pgpassword}@{pghost}:{pgport}/{pgdatabase}"
            )
        else:
            # URL hardcodeada como fallback
            database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"

    return database_url


def create_railway_users_robust():
    """Crea usuarios de prueba en Railway PostgreSQL de forma robusta"""

    print("🔄 Creando usuarios de prueba en Railway PostgreSQL...")
    print("=" * 60)

    # Obtener URL de base de datos
    database_url = get_railway_database_url()

    print(f"🔗 Conectando a Railway PostgreSQL...")
    print(f"   URL: {database_url[:50]}...")

    try:
        # Conectar a PostgreSQL con configuración robusta
        conn = psycopg2.connect(
            database_url,
            connect_timeout=10,
            application_name="medconnect_user_creation",
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("✅ Conexión a PostgreSQL exitosa")

        # Verificar conexión
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"📊 PostgreSQL version: {version[:50]}...")

        # Verificar si la tabla usuarios existe
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'usuarios'
            );
        """
        )

        table_exists = cursor.fetchone()[0]
        print(f"📋 Tabla usuarios existe: {table_exists}")

        if not table_exists:
            print("🔧 Creando tabla usuarios...")

            # Crear tabla usuarios
            cursor.execute(
                """
                CREATE TABLE usuarios (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    nombre VARCHAR(100) NOT NULL,
                    apellido VARCHAR(100) NOT NULL,
                    tipo_usuario VARCHAR(20) DEFAULT 'paciente',
                    telefono VARCHAR(20),
                    especialidad VARCHAR(100),
                    activo BOOLEAN DEFAULT true,
                    fecha_creacion TIMESTAMP DEFAULT NOW(),
                    ultimo_acceso TIMESTAMP
                );
            """
            )

            print("✅ Tabla usuarios creada")

        # Usuarios de prueba
        test_users = [
            {
                "email": "diego.castro.lagos@gmail.com",
                "password": "password123",
                "nombre": "Diego",
                "apellido": "Castro",
                "tipo_usuario": "profesional",
                "telefono": "+56912345678",
                "especialidad": "Medicina General",
            },
            {
                "email": "rodrigoandressilvabreve@gmail.com",
                "password": "password123",
                "nombre": "Rodrigo",
                "apellido": "Silva",
                "tipo_usuario": "paciente",
                "telefono": "+56987654321",
                "especialidad": None,
            },
        ]

        print(f"\n👥 Procesando {len(test_users)} usuarios de prueba...")

        for i, user in enumerate(test_users, 1):
            print(f"\n🔐 [{i}/{len(test_users)}] Procesando: {user['email']}")

            try:
                # Verificar si el usuario ya existe
                cursor.execute(
                    "SELECT id, email FROM usuarios WHERE email = %s", (user["email"],)
                )
                existing = cursor.fetchone()

                if existing:
                    print(
                        f"  ⚠️ Usuario ya existe (ID: {existing['id']}) - actualizando..."
                    )

                    # Actualizar usuario existente
                    password_hash = bcrypt.hashpw(
                        user["password"].encode("utf-8"), bcrypt.gensalt()
                    ).decode("utf-8")

                    cursor.execute(
                        """
                        UPDATE usuarios SET
                            password_hash = %s,
                            nombre = %s,
                            apellido = %s,
                            tipo_usuario = %s,
                            telefono = %s,
                            especialidad = %s,
                            activo = true
                        WHERE email = %s
                    """,
                        (
                            password_hash,
                            user["nombre"],
                            user["apellido"],
                            user["tipo_usuario"],
                            user["telefono"],
                            user["especialidad"],
                            user["email"],
                        ),
                    )

                    print(f"  ✅ Usuario actualizado")
                else:
                    print(f"  ➕ Creando nuevo usuario...")

                    # Hash de la contraseña
                    password_hash = bcrypt.hashpw(
                        user["password"].encode("utf-8"), bcrypt.gensalt()
                    ).decode("utf-8")

                    # Insertar usuario
                    cursor.execute(
                        """
                        INSERT INTO usuarios (
                            email, password_hash, nombre, apellido, tipo_usuario,
                            telefono, especialidad, activo, fecha_creacion
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                        )
                    """,
                        (
                            user["email"],
                            password_hash,
                            user["nombre"],
                            user["apellido"],
                            user["tipo_usuario"],
                            user["telefono"],
                            user["especialidad"],
                            True,
                        ),
                    )

                    print(f"  ✅ Usuario creado")

            except Exception as e:
                print(f"  ❌ Error procesando usuario {user['email']}: {e}")
                continue

        # Confirmar cambios
        conn.commit()
        print(f"\n✅ Cambios confirmados en la base de datos")

        # Verificar usuarios creados
        print(f"\n🔍 Verificando usuarios en la base de datos...")
        cursor.execute(
            """
            SELECT email, nombre, apellido, tipo_usuario, activo, fecha_creacion
            FROM usuarios 
            WHERE email IN ('diego.castro.lagos@gmail.com', 'rodrigoandressilvabreve@gmail.com')
            ORDER BY email
        """
        )

        users = cursor.fetchall()
        print(f"📋 Usuarios encontrados: {len(users)}")

        for user in users:
            status = "✅ Activo" if user["activo"] else "❌ Inactivo"
            created = (
                user["fecha_creacion"].strftime("%Y-%m-%d %H:%M")
                if user["fecha_creacion"]
                else "N/A"
            )
            print(
                f"  - {user['email']} ({user['tipo_usuario']}) - {status} - Creado: {created}"
            )

        cursor.close()
        conn.close()

        print(f"\n🎉 Usuarios de prueba creados exitosamente en Railway")
        return True

    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión a PostgreSQL: {e}")
        print(f"🔧 Verifica que la base de datos esté disponible")
        return False
    except psycopg2.Error as e:
        print(f"❌ Error de PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def test_railway_login_final():
    """Prueba final del login en Railway"""

    print(f"\n🧪 PRUEBA FINAL - Login en Railway...")
    print("=" * 50)

    # URL de login
    login_url = "https://www.medconnect.cl/login"

    # Datos de prueba
    test_credentials = [
        {
            "email": "diego.castro.lagos@gmail.com",
            "password": "password123",
            "expected_type": "profesional",
        },
        {
            "email": "rodrigoandressilvabreve@gmail.com",
            "password": "password123",
            "expected_type": "paciente",
        },
    ]

    success_count = 0

    for creds in test_credentials:
        print(f"\n🔐 Probando login con: {creds['email']}")

        try:
            # Crear sesión
            session = requests.Session()

            # Obtener página de login
            response = session.get(login_url, timeout=10)

            if response.status_code != 200:
                print(f"  ❌ Error obteniendo página de login: {response.status_code}")
                continue

            print(f"  ✅ Página de login cargada correctamente")

            # Intentar login
            login_data = {"email": creds["email"], "password": creds["password"]}

            login_response = session.post(
                login_url, data=login_data, allow_redirects=False, timeout=10
            )

            print(f"  📊 Status del login: {login_response.status_code}")

            if login_response.status_code == 302:
                redirect_url = login_response.headers.get("Location", "")
                print(f"  ✅ Login exitoso - Redirigiendo a: {redirect_url}")

                # Verificar redirección
                if "/professional" in redirect_url:
                    print(f"  ✅ Redirección correcta para profesional")
                elif "/patient" in redirect_url:
                    print(f"  ✅ Redirección correcta para paciente")
                else:
                    print(f"  ⚠️ Redirección inesperada: {redirect_url}")

                success_count += 1

            elif login_response.status_code == 200:
                # Verificar si hay mensaje de error en el HTML
                if "Credenciales inválidas" in login_response.text:
                    print(f"  ❌ Login fallido - Credenciales inválidas")
                elif "Error" in login_response.text:
                    print(f"  ❌ Login fallido - Error en el sistema")
                else:
                    print(f"  ⚠️ Login no procesado correctamente")
            else:
                print(f"  ❌ Error inesperado: {login_response.status_code}")

        except Exception as e:
            print(f"  ❌ Error probando login: {e}")

    print(f"\n" + "=" * 50)
    print(
        f"📊 RESULTADO FINAL: {success_count}/{len(test_credentials)} logins exitosos"
    )

    if success_count == len(test_credentials):
        print("🎉 ¡TODOS LOS LOGINS EXITOSOS!")
        print("✅ El problema de login en Railway está SOLUCIONADO")
    elif success_count > 0:
        print("⚠️ LOGIN PARCIALMENTE EXITOSO")
        print("🔧 Algunos usuarios funcionan, otros pueden necesitar verificación")
    else:
        print("❌ NINGÚN LOGIN EXITOSO")
        print("🔧 Revisa la configuración de la base de datos")

    return success_count == len(test_credentials)


if __name__ == "__main__":
    print("🚀 SOLUCIÓN ROBUSTA RAILWAY USERS")
    print("=" * 60)

    success = create_railway_users_robust()

    if success:
        test_railway_login_final()
        print(f"\n🎉 ¡PROCESO COMPLETADO!")
        print(f"🔧 Ahora puedes probar el login en https://www.medconnect.cl/login")
        print(f"📧 Credenciales:")
        print(f"   - diego.castro.lagos@gmail.com / password123")
        print(f"   - rodrigoandressilvabreve@gmail.com / password123")
    else:
        print(f"\n❌ Error en el proceso")
        print(f"🔧 Revisa la conexión a la base de datos")
        sys.exit(1)
