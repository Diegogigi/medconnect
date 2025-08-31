#!/usr/bin/env python3
"""
Script para crear tablas en PostgreSQL de Railway usando URL externa
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Crear todas las tablas necesarias"""

    # URL de conexión externa de Railway PostgreSQL
    DATABASE_URL = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"

    print("🚀 Conectando a PostgreSQL de Railway...")

    try:
        # Conectar usando la URL externa
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        print("✅ Conexión exitosa a PostgreSQL")

        # Crear tabla usuarios
        print("🔧 Creando tabla usuarios...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                tipo_usuario VARCHAR(20) NOT NULL CHECK (tipo_usuario IN ('paciente', 'profesional', 'admin')),
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activo BOOLEAN DEFAULT TRUE
            )
        """
        )

        # Crear tabla pacientes
        print("🔧 Creando tabla pacientes...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pacientes (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER REFERENCES usuarios(id),
                fecha_nacimiento DATE,
                genero VARCHAR(10),
                telefono VARCHAR(20),
                direccion TEXT,
                antecedentes_medicos TEXT,
                alergias TEXT,
                medicamentos_actuales TEXT
            )
        """
        )

        # Crear tabla profesionales
        print("🔧 Creando tabla profesionales...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS profesionales (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER REFERENCES usuarios(id),
                especialidad VARCHAR(100),
                numero_colegio VARCHAR(50),
                experiencia_anos INTEGER,
                horario_trabajo TEXT,
                telefono_consultorio VARCHAR(20),
                direccion_consultorio TEXT
            )
        """
        )

        # Crear tabla atenciones_medicas
        print("🔧 Creando tabla atenciones_medicas...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS atenciones_medicas (
                id SERIAL PRIMARY KEY,
                paciente_id INTEGER REFERENCES usuarios(id),
                profesional_id INTEGER REFERENCES usuarios(id),
                fecha_atencion DATE NOT NULL,
                hora_inicio TIME NOT NULL,
                hora_fin TIME,
                tipo_atencion VARCHAR(50),
                motivo_consulta TEXT,
                diagnostico TEXT,
                tratamiento TEXT,
                observaciones TEXT,
                estado VARCHAR(20) DEFAULT 'programada' CHECK (estado IN ('programada', 'en_proceso', 'completada', 'cancelada')),
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Crear tabla examenes
        print("🔧 Creando tabla examenes...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS examenes (
                id SERIAL PRIMARY KEY,
                paciente_id INTEGER REFERENCES usuarios(id),
                profesional_id INTEGER REFERENCES usuarios(id),
                nombre_examen VARCHAR(100) NOT NULL,
                tipo_examen VARCHAR(50),
                fecha_solicitud DATE DEFAULT CURRENT_DATE,
                fecha_realizacion DATE,
                resultado TEXT,
                archivo_url VARCHAR(500),
                estado VARCHAR(20) DEFAULT 'solicitado' CHECK (estado IN ('solicitado', 'en_proceso', 'completado', 'cancelado')),
                observaciones TEXT
            )
        """
        )

        # Crear tabla recetas
        print("🔧 Creando tabla recetas...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recetas (
                id SERIAL PRIMARY KEY,
                atencion_id INTEGER REFERENCES atenciones_medicas(id),
                paciente_id INTEGER REFERENCES usuarios(id),
                profesional_id INTEGER REFERENCES usuarios(id),
                fecha_emision DATE DEFAULT CURRENT_DATE,
                medicamentos TEXT,
                dosis TEXT,
                duracion_tratamiento VARCHAR(100),
                instrucciones TEXT,
                observaciones TEXT
            )
        """
        )

        # Commit de los cambios
        conn.commit()
        print("✅ Todas las tablas creadas exitosamente")

        # Insertar datos de prueba
        print("📝 Insertando datos de prueba...")

        # Usuario de prueba - Profesional
        cursor.execute(
            """
            INSERT INTO usuarios (email, password_hash, nombre, apellido, tipo_usuario)
            VALUES ('diego.castro.lagos@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3ZxQQxqKre', 'Diego', 'Castro', 'profesional')
            ON CONFLICT (email) DO NOTHING
        """
        )

        # Usuario de prueba - Paciente
        cursor.execute(
            """
            INSERT INTO usuarios (email, password_hash, nombre, apellido, tipo_usuario)
            VALUES ('paciente@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3ZxQQxqKre', 'Paciente', 'Test', 'paciente')
            ON CONFLICT (email) DO NOTHING
        """
        )

        conn.commit()
        print("✅ Datos de prueba insertados")

        # Listar tablas creadas
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

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Iniciando creación de tablas en PostgreSQL de Railway...")
    success = create_tables()

    if success:
        print("\n🎉 ¡Migración a PostgreSQL completada exitosamente!")
        print("🌐 Tu aplicación ahora usa PostgreSQL en Railway")
    else:
        print("\n❌ Error en la migración")
        sys.exit(1)
