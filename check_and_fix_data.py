#!/usr/bin/env python3
"""
Script para verificar y corregir datos en PostgreSQL
"""

import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"


def check_data():
    """Verificar datos existentes"""

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("🔍 Verificando datos existentes...")

        # Verificar usuarios
        cursor.execute("SELECT id, email, nombre, apellido, tipo_usuario FROM usuarios")
        usuarios = cursor.fetchall()
        print(f"👥 Usuarios encontrados: {len(usuarios)}")
        for user in usuarios:
            print(
                f"  - ID: {user['id']}, Email: {user['email']}, Tipo: {user['tipo_usuario']}"
            )

        # Verificar profesionales
        cursor.execute("SELECT id, email, nombre, apellido FROM profesionales")
        profesionales = cursor.fetchall()
        print(f"👨‍⚕️ Profesionales encontrados: {len(profesionales)}")
        for prof in profesionales:
            print(f"  - ID: {prof['id']}, Email: {prof['email']}")

        # Verificar tablas existentes
        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        )
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tablas disponibles: {tables}")

        cursor.close()
        conn.close()

        return usuarios, profesionales

    except Exception as e:
        print(f"❌ Error: {e}")
        return [], []


def insert_correct_data():
    """Insertar datos con referencias correctas"""

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        print("📝 Insertando datos corregidos...")

        # Obtener el ID del profesional existente
        cursor.execute(
            "SELECT id FROM profesionales WHERE email = 'diego.castro.lagos@gmail.com'"
        )
        result = cursor.fetchone()

        if result:
            profesional_id = result[0]
            print(f"✅ Profesional encontrado con ID: {profesional_id}")

            # Insertar pacientes con el ID correcto
            cursor.execute(
                """
                INSERT INTO pacientes_profesional (paciente_id, profesional_id, nombre_completo, rut, edad, fecha_nacimiento, genero, telefono, email, direccion, antecedentes_medicos, estado_relacion)
                VALUES 
                ('PAC_20250804_031213', %s, 'Giselle Arratia', '18145296-k', 34, '1992-06-25', 'Femenino', 56978784574, 'giselle.arratia@gmail.com', 'Pasaje El Boldo 8654, Pudahuel, Santiago', 'HTA, EPOC', 'activo'),
                ('PAC_20250804_003952', %s, 'Roberto Reyes', '17675599-8', 34, '1992-02-04', 'Masculino', 56971714520, 'r.reyes@gmail.com', 'Los Reyes 1452, depto 123, Las Condes', 'Diabetes, HTA, Lesión meniscal', 'activo')
                ON CONFLICT (paciente_id) DO NOTHING
            """,
                (profesional_id, profesional_id),
            )

            # Insertar horarios con el ID correcto
            cursor.execute(
                """
                INSERT INTO horarios_disponibles (profesional_id, dia_semana, hora_inicio, hora_fin, intervalo_minutos, estado)
                VALUES 
                (%s, 'Lunes', '09:00:00', '18:00:00', 30, 'Activo'),
                (%s, 'Martes', '09:00:00', '18:00:00', 30, 'Activo'),
                (%s, 'Miércoles', '09:00:00', '18:00:00', 30, 'Activo'),
                (%s, 'Jueves', '09:00:00', '18:00:00', 30, 'Activo'),
                (%s, 'Viernes', '09:00:00', '18:00:00', 30, 'Activo')
                ON CONFLICT DO NOTHING
            """,
                (
                    profesional_id,
                    profesional_id,
                    profesional_id,
                    profesional_id,
                    profesional_id,
                ),
            )

            conn.commit()
            print("✅ Datos insertados correctamente")

        else:
            print("❌ No se encontró el profesional")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🔍 Verificando estado de la base de datos...")
    usuarios, profesionales = check_data()

    if profesionales:
        print("\n📝 Corrigiendo datos...")
        insert_correct_data()
    else:
        print("❌ No hay profesionales para referenciar")
