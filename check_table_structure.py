#!/usr/bin/env python3
"""
Script para verificar la estructura real de las tablas
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_table_structure():
    """Verifica la estructura real de las tablas"""

    print("🔍 Verificando estructura de tablas...")

    try:
        # Obtener DATABASE_URL de Railway
        database_url = os.environ.get("DATABASE_URL")

        if not database_url:
            print("❌ DATABASE_URL no configurada")
            print("💡 Para probar localmente, configura las variables de entorno")
            return False

        print(f"🔗 Conectando a la base de datos...")

        # Conectar a la base de datos
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("✅ Conexión exitosa")

        # Verificar estructura de tabla profesionales
        print("\n📋 Estructura de tabla 'profesionales':")
        cursor.execute(
            """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'profesionales' 
            AND table_schema = 'public'
            ORDER BY ordinal_position;
        """
        )
        columns = cursor.fetchall()

        if columns:
            for col in columns:
                print(
                    f"   📝 {col['column_name']} ({col['data_type']}) - Nullable: {col['is_nullable']}"
                )
        else:
            print("   ❌ Tabla 'profesionales' no encontrada")

        # Verificar estructura de tabla pacientes_profesional
        print("\n📋 Estructura de tabla 'pacientes_profesional':")
        cursor.execute(
            """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'pacientes_profesional' 
            AND table_schema = 'public'
            ORDER BY ordinal_position;
        """
        )
        columns = cursor.fetchall()

        if columns:
            for col in columns:
                print(
                    f"   📝 {col['column_name']} ({col['data_type']}) - Nullable: {col['is_nullable']}"
                )
        else:
            print("   ❌ Tabla 'pacientes_profesional' no encontrada")

        # Verificar datos existentes
        print("\n📊 Datos existentes:")
        cursor.execute("SELECT COUNT(*) as count FROM profesionales")
        prof_count = cursor.fetchone()["count"]
        print(f"   👨‍⚕️ Profesionales: {prof_count}")

        cursor.execute("SELECT COUNT(*) as count FROM pacientes_profesional")
        pat_count = cursor.fetchone()["count"]
        print(f"   👤 Pacientes: {pat_count}")

        cursor.close()
        conn.close()

        print("\n✅ Verificación completada")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    check_table_structure()
