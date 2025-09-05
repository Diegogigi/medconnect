#!/usr/bin/env python3
"""
Script para diagnosticar el problema del método email_exists
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def debug_email_exists():
    """Diagnostica el problema del método email_exists"""

    print("🔍 Diagnosticando método email_exists...")

    # Obtener DATABASE_URL de Railway
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        print("❌ DATABASE_URL no configurada")
        print("💡 Para probar localmente, configura las variables de entorno")
        return False

    try:
        print(f"🔗 Conectando a la base de datos...")

        # Conectar a la base de datos
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("✅ Conexión exitosa")

        # 1. Verificar que la tabla usuarios existe
        print("\n1️⃣ Verificando tabla usuarios...")
        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'usuarios' 
            AND table_schema = 'public';
        """
        )
        table_exists = cursor.fetchone()

        if table_exists:
            print("   ✅ Tabla 'usuarios' existe")
        else:
            print("   ❌ Tabla 'usuarios' NO existe")
            return False

        # 2. Verificar estructura de la tabla usuarios
        print("\n2️⃣ Estructura de tabla usuarios:")
        cursor.execute(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'usuarios' 
            AND table_schema = 'public'
            ORDER BY ordinal_position;
        """
        )
        columns = cursor.fetchall()

        for col in columns:
            print(
                f"   📝 {col['column_name']} ({col['data_type']}) - Nullable: {col['is_nullable']}"
            )

        # 3. Verificar si hay datos en la tabla
        print("\n3️⃣ Datos en tabla usuarios:")
        cursor.execute("SELECT COUNT(*) as count FROM usuarios")
        count = cursor.fetchone()["count"]
        print(f"   📊 Total de usuarios: {count}")

        if count > 0:
            cursor.execute("SELECT email, nombre, tipo_usuario FROM usuarios LIMIT 3")
            users = cursor.fetchall()
            for user in users:
                print(
                    f"   👤 {user['email']} - {user['nombre']} ({user['tipo_usuario']})"
                )

        # 4. Probar consulta específica del método email_exists
        print("\n4️⃣ Probando consulta del método email_exists...")

        test_email = "test@example.com"
        query = "SELECT COUNT(*) FROM usuarios WHERE email = %s"

        try:
            cursor.execute(query, (test_email,))
            result = cursor.fetchone()
            count_result = result[0] if result else None

            print(f"   🔍 Email: {test_email}")
            print(f"   📊 Resultado: {count_result}")
            print(f"   📊 Tipo: {type(count_result)}")
            print(f"   ✅ Consulta ejecutada correctamente")

        except Exception as e:
            print(f"   ❌ Error en consulta: {e}")

        # 5. Verificar si hay algún trigger o constraint que pueda estar causando problemas
        print("\n5️⃣ Verificando triggers y constraints...")
        cursor.execute(
            """
            SELECT trigger_name, event_manipulation, action_statement
            FROM information_schema.triggers 
            WHERE event_object_table = 'usuarios';
        """
        )
        triggers = cursor.fetchall()

        if triggers:
            for trigger in triggers:
                print(
                    f"   ⚡ Trigger: {trigger['trigger_name']} - {trigger['event_manipulation']}"
                )
        else:
            print("   ✅ No hay triggers en la tabla usuarios")

        cursor.close()
        conn.close()

        print("\n✅ Diagnóstico completado")
        return True

    except Exception as e:
        print(f"❌ Error general: {e}")
        return False


if __name__ == "__main__":
    debug_email_exists()
