#!/usr/bin/env python3
"""
Script para diagnosticar el problema del endpoint de pacientes
"""

import psycopg2
from psycopg2.extras import RealDictCursor


def diagnose_patients_endpoint():
    """Diagnostica el problema del endpoint de pacientes"""

    print("🔍 Diagnosticando endpoint de pacientes...")
    print("=" * 60)

    # Conectar a Railway PostgreSQL
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("✅ Conexión exitosa")

        # 1. Verificar tabla pacientes_profesional
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
        table_exists = result[0] if result else False
        print(f"  📋 Tabla existe: {table_exists}")

        if table_exists:
            # Verificar estructura de la tabla
            cursor.execute(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'pacientes_profesional'
                ORDER BY ordinal_position;
            """
            )

            columns = cursor.fetchall()
            print(f"  📋 Columnas: {len(columns)}")
            for col in columns:
                print(f"    - {col['column_name']} ({col['data_type']})")

        # 2. Verificar usuarios profesionales
        print(f"\n2️⃣ Verificando usuarios profesionales...")
        cursor.execute(
            """
            SELECT id, email, nombre, apellido, tipo_usuario
            FROM usuarios 
            WHERE tipo_usuario = 'profesional'
            ORDER BY id;
        """
        )

        professionals = cursor.fetchall()
        print(f"  👥 Profesionales encontrados: {len(professionals)}")
        for prof in professionals:
            print(
                f"    - ID: {prof['id']}, {prof['nombre']} {prof['apellido']} ({prof['email']})"
            )

        # 3. Verificar relaciones en pacientes_profesional
        if table_exists:
            print(f"\n3️⃣ Verificando relaciones en pacientes_profesional...")
            cursor.execute(
                """
                SELECT 
                    pp.profesional_id,
                    pp.paciente_id,
                    pp.nombre_completo,
                    pp.estado_relacion
                FROM pacientes_profesional pp
                ORDER BY pp.profesional_id;
            """
            )

            relations = cursor.fetchall()
            print(f"  🔗 Relaciones encontradas: {len(relations)}")
            for rel in relations:
                print(
                    f"    - Profesional: {rel['profesional_id']}, Paciente: {rel['paciente_id']}, Estado: {rel['estado_relacion']}"
                )

        # 4. Probar consulta específica para Diego Castro (ID: 13)
        print(f"\n4️⃣ Probando consulta para Diego Castro (ID: 13)...")
        if table_exists:
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
                print(f"  📊 Resultados para Diego Castro: {len(result)}")

                if result:
                    for row in result:
                        print(
                            f"    - {row['nombre_completo']} ({row['email']}) - Estado: {row['estado_relacion']}"
                        )
                else:
                    print(f"    📋 No hay pacientes para Diego Castro")

            except Exception as e:
                print(f"  ❌ Error en consulta: {e}")

        # 5. Probar consulta para Giselle Arratia (ID: 19)
        print(f"\n5️⃣ Probando consulta para Giselle Arratia (ID: 19)...")
        if table_exists:
            try:
                cursor.execute(query, (19,))
                result = cursor.fetchall()
                print(f"  📊 Resultados para Giselle Arratia: {len(result)}")

                if result:
                    for row in result:
                        print(
                            f"    - {row['nombre_completo']} ({row['email']}) - Estado: {row['estado_relacion']}"
                        )
                else:
                    print(f"    📋 No hay pacientes para Giselle Arratia")

            except Exception as e:
                print(f"  ❌ Error en consulta: {e}")

        cursor.close()
        conn.close()

        print(f"\n🎉 Diagnóstico completado")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 DIAGNÓSTICO ENDPOINT PACIENTES")
    print("=" * 60)

    success = diagnose_patients_endpoint()

    if success:
        print(f"\n🎉 ¡Diagnóstico exitoso!")
        print(f"🔧 Revisa los resultados para identificar el problema")
    else:
        print(f"\n❌ Error en el diagnóstico")
        print(f"🔧 Revisa la conexión a la base de datos")
