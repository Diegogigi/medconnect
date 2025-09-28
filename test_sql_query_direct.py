#!/usr/bin/env python3
"""
Script para probar directamente la consulta SQL del endpoint
"""

import psycopg2
from psycopg2.extras import RealDictCursor


def test_sql_query_direct():
    """Prueba directamente la consulta SQL del endpoint"""

    print("🧪 Probando consulta SQL directamente...")
    print("=" * 60)

    # Conectar a Railway PostgreSQL
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("✅ Conexión exitosa")

        # 1. Verificar que la tabla existe
        print(f"\n1️⃣ Verificando tabla pacientes_profesional...")
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'pacientes_profesional'
            );
        """
        )

        result = cursor.fetchone()
        table_exists = result[0] if result and result[0] is not None else False
        print(f"  📊 Tabla existe: {table_exists}")

        if not table_exists:
            print(f"  ❌ La tabla pacientes_profesional no existe")
            return False

        # 2. Verificar datos en la tabla
        print(f"\n2️⃣ Verificando datos en la tabla...")
        cursor.execute(
            """
            SELECT COUNT(*) as total
            FROM pacientes_profesional;
        """
        )

        result = cursor.fetchone()
        total_records = result["total"] if result else 0
        print(f"  📊 Total registros: {total_records}")

        # 3. Verificar relaciones específicas
        print(f"\n3️⃣ Verificando relaciones para Diego Castro (ID: 13)...")
        cursor.execute(
            """
            SELECT profesional_id, paciente_id, nombre_completo, estado_relacion
            FROM pacientes_profesional
            WHERE profesional_id = 13;
        """
        )

        relations = cursor.fetchall()
        print(f"  📊 Relaciones para Diego Castro: {len(relations)}")
        for rel in relations:
            print(
                f"    - Prof: {rel['profesional_id']}, Paciente: {rel['paciente_id']}, Estado: {rel['estado_relacion']}"
            )

        # 4. Probar la consulta exacta del endpoint
        print(f"\n4️⃣ Probando consulta exacta del endpoint...")
        try:
            query = """
                SELECT DISTINCT 
                    pp.paciente_id as id,
                    pp.nombre_completo,
                    pp.email,
                    pp.telefono,
                    pp.fecha_nacimiento,
                    pp.genero,
                    pp.direccion,
                    pp.fecha_primera_consulta as fecha_primera_atencion,
                    pp.ultima_consulta as ultima_atencion,
                    pp.notas as notas_generales,
                    pp.estado_relacion
                FROM pacientes_profesional pp
                WHERE pp.profesional_id = %s 
                AND (pp.estado_relacion = 'activo' OR pp.estado_relacion IS NULL)
                ORDER BY pp.nombre_completo
            """

            cursor.execute(query, (13,))
            result = cursor.fetchall()
            print(f"  📊 Resultados de la consulta: {len(result)}")

            if result:
                for row in result:
                    print(
                        f"    - {row['nombre_completo']} ({row['email']}) - Estado: {row['estado_relacion']}"
                    )
            else:
                print(f"    📋 No hay resultados para Diego Castro")

        except Exception as e:
            print(f"  ❌ Error en consulta: {e}")
            print(f"  🔍 Tipo de error: {type(e).__name__}")
            return False

        # 5. Probar consulta simplificada
        print(f"\n5️⃣ Probando consulta simplificada...")
        try:
            simple_query = """
                SELECT paciente_id, nombre_completo, email, estado_relacion
                FROM pacientes_profesional
                WHERE profesional_id = %s;
            """

            cursor.execute(simple_query, (13,))
            result = cursor.fetchall()
            print(f"  📊 Resultados simplificados: {len(result)}")

            if result:
                for row in result:
                    print(
                        f"    - {row['paciente_id']}: {row['nombre_completo']} ({row['email']})"
                    )
            else:
                print(f"    📋 No hay resultados simplificados")

        except Exception as e:
            print(f"  ❌ Error en consulta simplificada: {e}")
            return False

        cursor.close()
        conn.close()

        print(f"\n🎉 Prueba completada")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 PRUEBA CONSULTA SQL DIRECTA")
    print("=" * 60)

    success = test_sql_query_direct()

    if success:
        print(f"\n🎉 ¡Consulta SQL funciona correctamente!")
        print(f"🔧 El problema puede estar en el código del endpoint")
    else:
        print(f"\n❌ Error en la consulta SQL")
        print(f"🔧 Revisa la estructura de la base de datos")
