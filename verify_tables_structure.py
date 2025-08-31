#!/usr/bin/env python3
"""
Script para verificar la estructura de todas las tablas
"""

import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"


def verify_structure():
    """Verificar estructura de todas las tablas"""

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("🔍 Verificando estructura de tablas...")

        # Obtener todas las tablas
        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        )
        tables = [row[0] for row in cursor.fetchall()]

        print(f"📋 Tablas encontradas: {tables}")

        # Verificar estructura de cada tabla
        for table in tables:
            print(f"\n🔧 Estructura de tabla: {table}")
            try:
                cursor.execute(
                    f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """
                )
                columns = cursor.fetchall()

                for col in columns:
                    print(
                        f"  - {col['column_name']}: {col['data_type']} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}"
                    )

            except Exception as e:
                print(f"  ❌ Error verificando {table}: {e}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    verify_structure()
