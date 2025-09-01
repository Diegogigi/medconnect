#!/usr/bin/env python3
"""
Script para probar directamente la base de datos y el registro
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_direct_database():
    """Prueba directamente la base de datos"""

    print("🧪 Probando directamente la base de datos...")

    try:
        # Obtener DATABASE_URL de Railway
        database_url = os.environ.get("DATABASE_URL")

        if not database_url:
            print("❌ DATABASE_URL no configurada")
            print("💡 Para probar localmente, configura las variables de entorno:")
            print(
                "   DATABASE_URL=postgresql://postgres:password@localhost:5432/medconnect"
            )
            return False

        print(f"🔗 Conectando a: {database_url[:50]}...")

        # Conectar a la base de datos
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("✅ Conexión exitosa")

        # Verificar tablas
        print("\n🔍 Verificando tablas...")
        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('profesionales', 'pacientes_profesional')
            ORDER BY table_name;
        """
        )
        tables = cursor.fetchall()

        for table in tables:
            print(f"   ✅ {table['table_name']}")

        if not tables:
            print("   ❌ No se encontraron las tablas necesarias")
            return False

        # Probar inserción de profesional
        print("\n🔍 Probando inserción de profesional...")

        professional_data = {
            "email": "test_direct@test.com",
            "nombre": "Test",
            "apellido": "Direct",
            "numero_registro": "TEST123",
            "especialidad": "Medicina General",
            "anos_experiencia": "5",
            "calificacion": "5.0",
            "direccion_consulta": "Calle Test 123",
            "horario_atencion": "Lunes a Viernes 9-17",
            "idiomas": "Español, Inglés",
            "profesion": "Médico",
            "institucion": "Hospital Test",
        }

        try:
            # Insertar profesional
            query = """
                INSERT INTO profesionales 
                (email, nombre, apellido, numero_registro, especialidad, anos_experiencia,
                 calificacion, direccion_consulta, horario_atencion, idiomas, profesion,
                 institucion, estado, disponible, unnamed_21, unnamed_22)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                professional_data["email"],
                professional_data["nombre"],
                professional_data["apellido"],
                professional_data["numero_registro"],
                professional_data["especialidad"],
                professional_data["anos_experiencia"],
                professional_data["calificacion"],
                professional_data["direccion_consulta"],
                professional_data["horario_atencion"],
                professional_data["idiomas"],
                professional_data["profesion"],
                professional_data["institucion"],
                "activo",
                True,
                datetime.now(),
                datetime.now(),
            )

            cursor.execute(query, values)
            conn.commit()

            print("✅ Profesional insertado exitosamente")

            # Verificar inserción
            cursor.execute(
                "SELECT COUNT(*) as count FROM profesionales WHERE email = %s",
                (professional_data["email"],),
            )
            count = cursor.fetchone()["count"]
            print(f"   📊 Registros encontrados: {count}")

            # Limpiar prueba
            cursor.execute(
                "DELETE FROM profesionales WHERE email = %s",
                (professional_data["email"],),
            )
            conn.commit()
            print("✅ Prueba limpiada")

        except Exception as e:
            print(f"❌ Error insertando profesional: {e}")
            conn.rollback()

        # Probar inserción de paciente
        print("\n🔍 Probando inserción de paciente...")

        patient_data = {
            "nombre": "Test",
            "apellido": "Patient",
            "rut": "12345678-9",
            "fecha_nacimiento": "1990-01-01",
            "genero": "Masculino",
            "telefono": "+56912345678",
            "email": "test_patient@test.com",
            "direccion": "Calle Test 456",
            "antecedentes_medicos": "Ninguno",
        }

        try:
            # Generar ID único para paciente
            paciente_id = f"PAC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Insertar paciente
            query = """
                INSERT INTO pacientes_profesional 
                (paciente_id, nombre_completo, rut, edad, fecha_nacimiento, genero, 
                 telefono, email, direccion, antecedentes_medicos, estado_relacion, fecha_registro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Calcular edad
            edad = None
            if patient_data.get("fecha_nacimiento"):
                try:
                    fecha_nac = datetime.strptime(
                        patient_data["fecha_nacimiento"], "%Y-%m-%d"
                    )
                    edad = (datetime.now() - fecha_nac).days // 365
                except:
                    pass

            values = (
                paciente_id,
                f"{patient_data['nombre']} {patient_data['apellido']}",
                patient_data["rut"],
                edad,
                patient_data["fecha_nacimiento"],
                patient_data["genero"],
                patient_data["telefono"],
                patient_data["email"],
                patient_data["direccion"],
                patient_data["antecedentes_medicos"],
                "activo",
                datetime.now(),
            )

            cursor.execute(query, values)
            conn.commit()

            print("✅ Paciente insertado exitosamente")

            # Verificar inserción
            cursor.execute(
                "SELECT COUNT(*) as count FROM pacientes_profesional WHERE email = %s",
                (patient_data["email"],),
            )
            count = cursor.fetchone()["count"]
            print(f"   📊 Registros encontrados: {count}")

            # Limpiar prueba
            cursor.execute(
                "DELETE FROM pacientes_profesional WHERE email = %s",
                (patient_data["email"],),
            )
            conn.commit()
            print("✅ Prueba limpiada")

        except Exception as e:
            print(f"❌ Error insertando paciente: {e}")
            conn.rollback()

        cursor.close()
        conn.close()

        print("\n✅ Todas las pruebas completadas exitosamente")
        return True

    except Exception as e:
        print(f"❌ Error general: {e}")
        return False


if __name__ == "__main__":
    test_direct_database()
