#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para migrar MedConnect de Google Sheets a PostgreSQL en Railway
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import logging
from datetime import datetime
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgreSQLMigration:
    def __init__(self):
        """Inicializar conexión a PostgreSQL"""
        self.conn = None
        self.cursor = None

    def connect_to_railway_postgres(self):
        """Conectar a PostgreSQL en Railway"""
        try:
            # Railway automáticamente proporciona estas variables de entorno
            database_url = os.environ.get("DATABASE_URL")

            if database_url:
                # Railway proporciona DATABASE_URL completa
                self.conn = psycopg2.connect(database_url)
            else:
                # Conectar usando variables individuales (backup)
                self.conn = psycopg2.connect(
                    host=os.environ.get("PGHOST", "localhost"),
                    database=os.environ.get("PGDATABASE", "medconnect"),
                    user=os.environ.get("PGUSER", "postgres"),
                    password=os.environ.get("PGPASSWORD", ""),
                    port=os.environ.get("PGPORT", "5432"),
                )

            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logger.info("✅ Conectado a PostgreSQL exitosamente")
            return True

        except Exception as e:
            logger.error(f"❌ Error conectando a PostgreSQL: {e}")
            return False

    def create_tables(self):
        """Crear todas las tablas necesarias"""
        logger.info("🔧 Creando tablas...")

        # Tabla de usuarios
        usuarios_sql = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            tipo_usuario VARCHAR(20) NOT NULL CHECK (tipo_usuario IN ('profesional', 'paciente', 'admin')),
            telefono VARCHAR(20),
            ciudad VARCHAR(100),
            direccion TEXT,
            fecha_nacimiento DATE,
            genero VARCHAR(20),
            estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'suspendido')),
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultimo_acceso TIMESTAMP,
            fecha_cambio_password TIMESTAMP,
            
            -- Campos específicos para profesionales
            especialidad VARCHAR(100),
            numero_colegiado VARCHAR(50),
            hospital VARCHAR(200),
            anos_experiencia INTEGER,
            
            -- Índices
            CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
        );
        
        CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
        CREATE INDEX IF NOT EXISTS idx_usuarios_tipo ON usuarios(tipo_usuario);
        CREATE INDEX IF NOT EXISTS idx_usuarios_estado ON usuarios(estado);
        """

        # Tabla de atenciones médicas
        atenciones_sql = """
        CREATE TABLE IF NOT EXISTS atenciones_medicas (
            id SERIAL PRIMARY KEY,
            profesional_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            paciente_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            fecha_atencion DATE NOT NULL,
            hora_inicio TIME NOT NULL,
            hora_fin TIME,
            tipo_atencion VARCHAR(50) NOT NULL,
            motivo_consulta TEXT,
            diagnostico TEXT,
            tratamiento TEXT,
            observaciones TEXT,
            estado VARCHAR(20) DEFAULT 'programada' CHECK (estado IN ('programada', 'en_curso', 'completada', 'cancelada')),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_atenciones_profesional ON atenciones_medicas(profesional_id);
        CREATE INDEX IF NOT EXISTS idx_atenciones_paciente ON atenciones_medicas(paciente_id);
        CREATE INDEX IF NOT EXISTS idx_atenciones_fecha ON atenciones_medicas(fecha_atencion);
        """

        # Tabla de agenda/citas
        agenda_sql = """
        CREATE TABLE IF NOT EXISTS agenda_citas (
            id SERIAL PRIMARY KEY,
            profesional_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            paciente_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
            fecha DATE NOT NULL,
            hora_inicio TIME NOT NULL,
            hora_fin TIME NOT NULL,
            disponible BOOLEAN DEFAULT TRUE,
            tipo_cita VARCHAR(50),
            notas TEXT,
            estado VARCHAR(20) DEFAULT 'disponible' CHECK (estado IN ('disponible', 'reservada', 'confirmada', 'completada', 'cancelada')),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_agenda_profesional ON agenda_citas(profesional_id);
        CREATE INDEX IF NOT EXISTS idx_agenda_fecha ON agenda_citas(fecha);
        CREATE INDEX IF NOT EXISTS idx_agenda_disponible ON agenda_citas(disponible);
        """

        # Tabla de archivos médicos
        archivos_medicos_sql = """
        CREATE TABLE IF NOT EXISTS archivos_medicos (
            id SERIAL PRIMARY KEY,
            paciente_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            profesional_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
            atencion_id INTEGER REFERENCES atenciones_medicas(id) ON DELETE SET NULL,
            nombre_archivo VARCHAR(255) NOT NULL,
            ruta_archivo VARCHAR(500) NOT NULL,
            tipo_archivo VARCHAR(50),
            tamaño_archivo INTEGER,
            descripcion TEXT,
            fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'archivado', 'eliminado'))
        );
        
        CREATE INDEX IF NOT EXISTS idx_archivos_paciente ON archivos_medicos(paciente_id);
        CREATE INDEX IF NOT EXISTS idx_archivos_profesional ON archivos_medicos(profesional_id);
        """

        try:
            # Ejecutar todas las consultas
            self.cursor.execute(usuarios_sql)
            self.cursor.execute(atenciones_sql)
            self.cursor.execute(agenda_sql)
            self.cursor.execute(archivos_medicos_sql)

            self.conn.commit()
            logger.info("✅ Tablas creadas exitosamente")
            return True

        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")
            self.conn.rollback()
            return False

    def insert_sample_data(self):
        """Insertar datos de ejemplo"""
        logger.info("📝 Insertando datos de ejemplo...")

        try:
            # Hash para contraseña "password123"
            password_hash = bcrypt.hashpw(
                "password123".encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            # Insertar usuarios de ejemplo
            usuarios_data = [
                {
                    "nombre": "Diego",
                    "apellido": "Castro",
                    "email": "diego.castro.lagos@gmail.com",
                    "password_hash": password_hash,
                    "tipo_usuario": "profesional",
                    "telefono": "+56979712175",
                    "ciudad": "Talcahuano",
                    "especialidad": "Medicina General",
                    "numero_colegiado": "MED-001",
                    "hospital": "Hospital Regional",
                    "anos_experiencia": 10,
                },
                {
                    "nombre": "Juan",
                    "apellido": "Pérez",
                    "email": "paciente@test.com",
                    "password_hash": password_hash,
                    "tipo_usuario": "paciente",
                    "telefono": "+56912345678",
                    "ciudad": "Santiago",
                    "fecha_nacimiento": "1990-05-15",
                    "genero": "Masculino",
                    "direccion": "Av. Providencia 123, Santiago",
                },
                {
                    "nombre": "María",
                    "apellido": "González",
                    "email": "maria.gonzalez@test.com",
                    "password_hash": password_hash,
                    "tipo_usuario": "paciente",
                    "telefono": "+56987654321",
                    "ciudad": "Santiago",
                    "fecha_nacimiento": "1985-12-20",
                    "genero": "Femenino",
                    "direccion": "Calle Las Condes 456, Santiago",
                },
            ]

            for user_data in usuarios_data:
                # Verificar si el usuario ya existe
                self.cursor.execute(
                    "SELECT id FROM usuarios WHERE email = %s", (user_data["email"],)
                )
                if not self.cursor.fetchone():
                    # Construir query dinámicamente
                    columns = ", ".join(user_data.keys())
                    placeholders = ", ".join(["%s"] * len(user_data))
                    query = f"INSERT INTO usuarios ({columns}) VALUES ({placeholders}) RETURNING id"

                    self.cursor.execute(query, list(user_data.values()))
                    user_id = self.cursor.fetchone()["id"]
                    logger.info(
                        f"✅ Usuario creado: {user_data['email']} (ID: {user_id})"
                    )

            # Insertar datos de agenda de ejemplo
            agenda_data = [
                {
                    "profesional_id": 1,  # Diego Castro
                    "fecha": "2025-08-31",
                    "hora_inicio": "09:00",
                    "hora_fin": "17:00",
                    "disponible": True,
                    "notas": "Horario normal de atención",
                },
                {
                    "profesional_id": 1,
                    "fecha": "2025-09-01",
                    "hora_inicio": "09:00",
                    "hora_fin": "17:00",
                    "disponible": True,
                    "notas": "Horario normal de atención",
                },
            ]

            for agenda_item in agenda_data:
                columns = ", ".join(agenda_item.keys())
                placeholders = ", ".join(["%s"] * len(agenda_item))
                query = f"INSERT INTO agenda_citas ({columns}) VALUES ({placeholders})"
                self.cursor.execute(query, list(agenda_item.values()))

            self.conn.commit()
            logger.info("✅ Datos de ejemplo insertados exitosamente")
            return True

        except Exception as e:
            logger.error(f"❌ Error insertando datos: {e}")
            self.conn.rollback()
            return False

    def test_connection(self):
        """Probar la conexión y consultas básicas"""
        logger.info("🧪 Probando conexión y consultas...")

        try:
            # Probar consulta de usuarios
            self.cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            total_users = self.cursor.fetchone()["total"]
            logger.info(f"📊 Total de usuarios en la base de datos: {total_users}")

            # Probar consulta de profesionales
            self.cursor.execute(
                "SELECT nombre, apellido, email FROM usuarios WHERE tipo_usuario = 'profesional'"
            )
            profesionales = self.cursor.fetchall()
            logger.info(f"👨‍⚕️ Profesionales encontrados: {len(profesionales)}")
            for prof in profesionales:
                logger.info(
                    f"  - {prof['nombre']} {prof['apellido']} ({prof['email']})"
                )

            # Probar consulta de pacientes
            self.cursor.execute(
                "SELECT nombre, apellido, email FROM usuarios WHERE tipo_usuario = 'paciente'"
            )
            pacientes = self.cursor.fetchall()
            logger.info(f"🏥 Pacientes encontrados: {len(pacientes)}")
            for pac in pacientes:
                logger.info(f"  - {pac['nombre']} {pac['apellido']} ({pac['email']})")

            return True

        except Exception as e:
            logger.error(f"❌ Error en pruebas: {e}")
            return False

    def close_connection(self):
        """Cerrar conexión"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("🔒 Conexión cerrada")


def main():
    """Función principal"""
    logger.info("🚀 Iniciando migración a PostgreSQL...")

    migration = PostgreSQLMigration()

    try:
        # Paso 1: Conectar
        if not migration.connect_to_railway_postgres():
            logger.error("❌ No se pudo conectar a PostgreSQL")
            return False

        # Paso 2: Crear tablas
        if not migration.create_tables():
            logger.error("❌ No se pudieron crear las tablas")
            return False

        # Paso 3: Insertar datos de ejemplo
        if not migration.insert_sample_data():
            logger.error("❌ No se pudieron insertar los datos")
            return False

        # Paso 4: Probar conexión
        if not migration.test_connection():
            logger.error("❌ Las pruebas fallaron")
            return False

        logger.info("🎉 ¡Migración completada exitosamente!")
        logger.info("💡 Ahora puedes usar PostgreSQL en lugar de Google Sheets")

        return True

    except Exception as e:
        logger.error(f"❌ Error durante la migración: {e}")
        return False

    finally:
        migration.close_connection()


if __name__ == "__main__":
    main()
