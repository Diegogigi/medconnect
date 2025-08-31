#!/usr/bin/env python3
"""
Script para agregar las tablas faltantes a PostgreSQL de Railway
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_missing_tables():
    """Agregar solo las tablas que faltan"""

    # URL de conexión externa de Railway PostgreSQL
    DATABASE_URL = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"

    print("🚀 Conectando a PostgreSQL de Railway...")

    try:
        # Conectar usando la URL externa
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        print("✅ Conexión exitosa a PostgreSQL")

        # ==================== TABLA CITAS_AGENDA ====================
        print("🔧 Creando tabla citas_agenda...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS citas_agenda (
                cita_id TEXT PRIMARY KEY,
                fecha DATE NOT NULL,
                hora TIME NOT NULL,
                paciente_id TEXT,
                paciente_nombre TEXT,
                paciente_rut TEXT,
                tipo_atencion TEXT,
                estado TEXT DEFAULT 'pendiente',
                motivo TEXT,
                profesional_id INTEGER,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # ==================== TABLA PACIENTES_PROFESIONAL ====================
        print("🔧 Creando tabla pacientes_profesional...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pacientes_profesional (
                paciente_id TEXT PRIMARY KEY,
                profesional_id INTEGER,
                nombre_completo TEXT NOT NULL,
                rut TEXT,
                edad BIGINT,
                fecha_nacimiento DATE,
                genero TEXT,
                telefono NUMERIC,
                email TEXT,
                direccion TEXT,
                antecedentes_medicos TEXT,
                fecha_primera_consulta TIMESTAMP,
                ultima_consulta TIMESTAMP,
                num_atenciones BIGINT DEFAULT 0,
                estado_relacion TEXT DEFAULT 'activo',
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notas TEXT
            )
        """
        )

        # ==================== TABLA ATENCIONES_MEDICAS ====================
        print("🔧 Creando tabla atenciones_medicas...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS atenciones_medicas (
                atencion_id TEXT PRIMARY KEY,
                profesional_id INTEGER,
                profesional_nombre TEXT,
                paciente_id TEXT,
                paciente_nombre TEXT,
                paciente_rut TEXT,
                paciente_edad BIGINT,
                fecha_hora TIMESTAMP NOT NULL,
                tipo_atencion TEXT,
                motivo_consulta TEXT,
                diagnostico TEXT,
                tratamiento TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                estado TEXT DEFAULT 'completada',
                requiere_seguimiento BOOLEAN DEFAULT FALSE,
                tiene_archivos TEXT DEFAULT 'No'
            )
        """
        )

        # ==================== TABLA ARCHIVOS_ADJUNTOS ====================
        print("🔧 Creando tabla archivos_adjuntos...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS archivos_adjuntos (
                archivo_id TEXT PRIMARY KEY,
                atencion_id TEXT,
                nombre_archivo TEXT NOT NULL,
                tipo_archivo TEXT,
                ruta_archivo TEXT,
                fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                estado TEXT DEFAULT 'activo'
            )
        """
        )

        # ==================== TABLA HORARIOS_PROFESIONAL ====================
        print("🔧 Creando tabla horarios_profesional...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS horarios_profesional (
                id BIGSERIAL PRIMARY KEY,
                profesional_id INTEGER,
                dia_semana TEXT NOT NULL,
                hora_inicio TIME NOT NULL,
                hora_fin TIME NOT NULL,
                disponible BOOLEAN DEFAULT TRUE
            )
        """
        )

        # ==================== TABLA HORARIOS_DISPONIBLES ====================
        print("🔧 Creando tabla horarios_disponibles...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS horarios_disponibles (
                id BIGSERIAL PRIMARY KEY,
                profesional_id INTEGER,
                dia_semana TEXT NOT NULL,
                hora_inicio TIME NOT NULL,
                hora_fin TIME NOT NULL,
                intervalo_minutos BIGINT DEFAULT 30,
                estado TEXT DEFAULT 'Activo'
            )
        """
        )

        # ==================== TABLA RECORDATORIOS_PROFESIONAL ====================
        print("🔧 Creando tabla recordatorios_profesional...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recordatorios_profesional (
                recordatorio_id TEXT PRIMARY KEY,
                profesional_id INTEGER,
                tipo TEXT,
                paciente_id TEXT,
                titulo TEXT NOT NULL,
                mensaje TEXT,
                fecha DATE NOT NULL,
                hora TIME,
                prioridad TEXT DEFAULT 'media',
                repetir BOOLEAN DEFAULT FALSE,
                tipo_repeticion TEXT,
                estado TEXT DEFAULT 'activo',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # ==================== TABLA SESIONES ====================
        print("🔧 Creando tabla sesiones...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sesiones (
                id TEXT PRIMARY KEY,
                atencion_id TEXT,
                fecha_sesion TIMESTAMP NOT NULL,
                duracion BIGINT,
                tipo_sesion TEXT,
                objetivos TEXT,
                actividades TEXT,
                observaciones TEXT,
                progreso TEXT,
                estado TEXT DEFAULT 'completada',
                recomendaciones TEXT,
                proxima_sesion TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                profesional_id INTEGER
            )
        """
        )

        # ==================== TABLA INTERACCIONES_BOT ====================
        print("🔧 Creando tabla interacciones_bot...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS interacciones_bot (
                id NUMERIC PRIMARY KEY,
                user_id NUMERIC,
                username TEXT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action_type TEXT,
                status TEXT DEFAULT 'processed',
                unnamed_8 TEXT,
                unnamed_10 TIMESTAMP,
                unnamed_11 TEXT,
                unnamed_12 TEXT
            )
        """
        )

        # ==================== TABLAS ADICIONALES ====================
        print("🔧 Creando tablas adicionales...")

        # Medicamentos
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS medicamentos (
                id BIGSERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                principio_activo TEXT,
                dosis TEXT,
                presentacion TEXT,
                laboratorio TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Examenes
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS examenes (
                id BIGSERIAL PRIMARY KEY,
                nombre_examen TEXT NOT NULL,
                tipo_examen TEXT,
                descripcion TEXT,
                preparacion TEXT,
                duracion INTEGER,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Agenda
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agenda (
                id BIGSERIAL PRIMARY KEY,
                profesional_id INTEGER,
                fecha DATE NOT NULL,
                hora_inicio TIME NOT NULL,
                hora_fin TIME NOT NULL,
                disponible BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Especialidades
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS especialidades (
                id BIGSERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                activa BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Familiares_Autorizados
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS familiares_autorizados (
                id BIGSERIAL PRIMARY KEY,
                paciente_id TEXT,
                nombre TEXT NOT NULL,
                relacion TEXT,
                telefono TEXT,
                email TEXT,
                autorizado BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Recordatorios
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recordatorios (
                id BIGSERIAL PRIMARY KEY,
                usuario_id INTEGER,
                titulo TEXT NOT NULL,
                mensaje TEXT,
                fecha DATE NOT NULL,
                hora TIME,
                prioridad TEXT DEFAULT 'media',
                completado BOOLEAN DEFAULT FALSE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Logs_Acceso
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS logs_acceso (
                id BIGSERIAL PRIMARY KEY,
                usuario_id INTEGER,
                fecha_acceso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                accion TEXT,
                resultado TEXT
            )
        """
        )

        # Commit de los cambios
        conn.commit()
        print("✅ Todas las tablas adicionales creadas exitosamente")

        # Insertar datos de prueba en las nuevas tablas
        print("📝 Insertando datos de prueba...")

        # Pacientes de prueba
        cursor.execute(
            """
            INSERT INTO pacientes_profesional (paciente_id, profesional_id, nombre_completo, rut, edad, fecha_nacimiento, genero, telefono, email, direccion, antecedentes_medicos, estado_relacion)
            VALUES 
            ('PAC_20250804_031213', 1, 'Giselle Arratia', '18145296-k', 34, '1992-06-25', 'Femenino', 56978784574, 'giselle.arratia@gmail.com', 'Pasaje El Boldo 8654, Pudahuel, Santiago', 'HTA, EPOC', 'activo'),
            ('PAC_20250804_003952', 1, 'Roberto Reyes', '17675599-8', 34, '1992-02-04', 'Masculino', 56971714520, 'r.reyes@gmail.com', 'Los Reyes 1452, depto 123, Las Condes', 'Diabetes, HTA, Lesión meniscal', 'activo')
            ON CONFLICT (paciente_id) DO NOTHING
        """
        )

        # Horarios disponibles
        cursor.execute(
            """
            INSERT INTO horarios_disponibles (profesional_id, dia_semana, hora_inicio, hora_fin, intervalo_minutos, estado)
            VALUES 
            (1, 'Lunes', '09:00:00', '18:00:00', 30, 'Activo'),
            (1, 'Martes', '09:00:00', '18:00:00', 30, 'Activo'),
            (1, 'Miércoles', '09:00:00', '18:00:00', 30, 'Activo'),
            (1, 'Jueves', '09:00:00', '18:00:00', 30, 'Activo'),
            (1, 'Viernes', '09:00:00', '18:00:00', 30, 'Activo')
            ON CONFLICT DO NOTHING
        """
        )

        conn.commit()
        print("✅ Datos de prueba insertados")

        # Listar todas las tablas
        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        )

        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Todas las tablas disponibles: {tables}")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Agregando tablas faltantes a PostgreSQL de Railway...")
    success = add_missing_tables()

    if success:
        print("\n🎉 ¡Todas las tablas agregadas exitosamente!")
        print("🌐 Base de datos completa y lista para producción")
    else:
        print("\n❌ Error al agregar las tablas")
        sys.exit(1)
