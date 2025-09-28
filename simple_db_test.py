#!/usr/bin/env python3
"""
Script simple para probar la base de datos
"""

import psycopg2
from psycopg2.extras import RealDictCursor


def simple_db_test():
    """Prueba simple de la base de datos"""

    print("🔍 Prueba simple de la base de datos...")
    print("=" * 60)

    # Conectar a Railway PostgreSQL
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("✅ Conexión exitosa")

        # 1. Listar tablas
        print(f"\n1️⃣ Listando tablas...")
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """
        )

        tables = cursor.fetchall()
        print(f"  📊 Tablas encontradas: {len(tables)}")
        for table in tables:
            print(f"    - {table['table_name']}")

        # 2. Verificar si existe pacientes_profesional
        pacientes_table_exists = any(
            table["table_name"] == "pacientes_profesional" for table in tables
        )
        print(f"  📊 Tabla pacientes_profesional existe: {pacientes_table_exists}")

        if pacientes_table_exists:
            # 3. Contar registros
            print(f"\n2️⃣ Contando registros...")
            cursor.execute("SELECT COUNT(*) as total FROM pacientes_profesional;")
            result = cursor.fetchone()
            total = result["total"] if result else 0
            print(f"  📊 Total registros: {total}")

            # 4. Mostrar algunos registros
            print(f"\n3️⃣ Mostrando registros...")
            cursor.execute(
                """
                SELECT profesional_id, paciente_id, nombre_completo, estado_relacion
                FROM pacientes_profesional
                LIMIT 5;
            """
            )

            records = cursor.fetchall()
            print(f"  📊 Registros encontrados: {len(records)}")
            for record in records:
                print(
                    f"    - Prof: {record['profesional_id']}, Paciente: {record['paciente_id']}, Estado: {record['estado_relacion']}"
                )

        cursor.close()
        conn.close()

        print(f"\n🎉 Prueba completada")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 PRUEBA SIMPLE BASE DE DATOS")
    print("=" * 60)

    success = simple_db_test()

    if success:
        print(f"\n🎉 ¡Prueba exitosa!")
    else:
        print(f"\n❌ Error en la prueba")
