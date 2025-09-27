#!/usr/bin/env python3
"""
Script para crear usuarios de prueba en Railway PostgreSQL
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import requests


def create_railway_users():
    """Crea usuarios de prueba en Railway PostgreSQL"""

    print("🔄 Creando usuarios de prueba en Railway PostgreSQL...")
    print("=" * 60)

    # Variables de conexión a Railway
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"

    print(f"🔗 Conectando a Railway PostgreSQL...")
    print(f"   URL: {database_url[:50]}...")

    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("✅ Conexión a PostgreSQL exitosa")

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

        if not table_exists:
            print("❌ La tabla 'usuarios' no existe")
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

        print(f"\n👥 Creando {len(test_users)} usuarios de prueba...")

        for user in test_users:
            print(f"\n🔐 Procesando: {user['email']}")

            # Verificar si el usuario ya existe
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (user["email"],))
            existing = cursor.fetchone()

            if existing:
                print(f"  ⚠️ Usuario ya existe - actualizando...")

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

        # Confirmar cambios
        conn.commit()

        # Verificar usuarios creados
        print(f"\n🔍 Verificando usuarios creados...")
        cursor.execute(
            """
            SELECT email, nombre, apellido, tipo_usuario, activo 
            FROM usuarios 
            WHERE email IN ('diego.castro.lagos@gmail.com', 'rodrigoandressilvabreve@gmail.com')
        """
        )

        users = cursor.fetchall()
        print(f"📋 Usuarios encontrados: {len(users)}")

        for user in users:
            status = "✅ Activo" if user["activo"] else "❌ Inactivo"
            print(f"  - {user['email']} ({user['tipo_usuario']}) - {status}")

        cursor.close()
        conn.close()

        print(f"\n🎉 Usuarios de prueba creados exitosamente en Railway")
        return True

    except Exception as e:
        print(f"❌ Error creando usuarios: {e}")
        return False


def test_railway_login_after_creation():
    """Prueba el login después de crear los usuarios"""

    print(f"\n🧪 Probando login después de crear usuarios...")
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

    for creds in test_credentials:
        print(f"\n🔐 Probando login con: {creds['email']}")

        try:
            # Crear sesión
            session = requests.Session()

            # Obtener página de login
            response = session.get(login_url)

            if response.status_code != 200:
                print(f"  ❌ Error obteniendo página de login: {response.status_code}")
                continue

            print(f"  ✅ Página de login cargada correctamente")

            # Intentar login
            login_data = {"email": creds["email"], "password": creds["password"]}

            login_response = session.post(
                login_url, data=login_data, allow_redirects=False
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
    print("📋 Resumen de pruebas:")
    print("1. Si todos los logins son exitosos: ✅ Sistema funcionando")
    print("2. Si hay errores de credenciales: ❌ Problema de base de datos")
    print("3. Si hay errores 500: ❌ Problema de configuración")
    print("4. Si hay timeouts: ⏰ Aplicación no responde")


if __name__ == "__main__":
    print("🚀 CREACIÓN USUARIOS RAILWAY")
    print("=" * 60)

    success = create_railway_users()

    if success:
        test_railway_login_after_creation()
        print(f"\n🎉 ¡Proceso completado!")
        print(f"🔧 Ahora puedes probar el login en https://www.medconnect.cl/login")
    else:
        print(f"\n❌ Error en el proceso")
        print(f"🔧 Revisa la conexión a la base de datos")
