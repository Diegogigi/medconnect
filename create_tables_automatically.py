#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script AUTOMÁTICO para crear todas las tablas en PostgreSQL
Basado en la estructura de bd_medconnect
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AutoTableCreator:
    def __init__(self):
        """Inicializar conexión a PostgreSQL"""
        self.conn = None
        self.cursor = None

    def connect_to_postgresql(self):
        """Conectar a PostgreSQL en Railway"""
        try:
            # Railway proporciona DATABASE_URL automáticamente
            database_url = os.environ.get("DATABASE_URL")

            if database_url:
                logger.info("🔗 Conectando usando DATABASE_URL...")
                self.conn = psycopg2.connect(database_url)
            else:
                # Variables individuales como backup
                logger.info("🔗 Conectando usando variables individuales...")
                self.conn = psycopg2.connect(
                    host=os.environ.get("PGHOST", "localhost"),
                    database=os.environ.get("PGDATABASE", "railway"),
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

    def create_all_tables(self):
        """Crear TODAS las tablas automáticamente"""
        logger.info("🏗️ Creando todas las tablas automáticamente...")

        # 1. TABLA USUARIOS (profesionales y pacientes)
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
            
            -- Validación de email
            CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
        );
        
        -- Índices para usuarios
        CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
        CREATE INDEX IF NOT EXISTS idx_usuarios_tipo ON usuarios(tipo_usuario);
        CREATE INDEX IF NOT EXISTS idx_usuarios_estado ON usuarios(estado);
        """

        # 2. TABLA ATENCIONES MÉDICAS
        atenciones_sql = """
        CREATE TABLE IF NOT EXISTS atenciones_medicas (
            id SERIAL PRIMARY KEY,
            atencion_id VARCHAR(50) UNIQUE,
            profesional_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            paciente_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            profesional_nombre VARCHAR(200),
            paciente_nombre VARCHAR(200),
            paciente_rut VARCHAR(20),
            paciente_edad INTEGER,
            fecha_atencion DATE NOT NULL,
            hora_inicio TIME NOT NULL,
            hora_fin TIME,
            fecha_hora TIMESTAMP,
            tipo_atencion VARCHAR(50) NOT NULL,
            motivo_consulta TEXT,
            diagnostico TEXT,
            tratamiento TEXT,
            observaciones TEXT,
            estado VARCHAR(20) DEFAULT 'programada' CHECK (estado IN ('programada', 'en_curso', 'completada', 'cancelada')),
            requiere_seguimiento BOOLEAN DEFAULT FALSE,
            tiene_archivos BOOLEAN DEFAULT FALSE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Índices para atenciones
        CREATE INDEX IF NOT EXISTS idx_atenciones_profesional ON atenciones_medicas(profesional_id);
        CREATE INDEX IF NOT EXISTS idx_atenciones_paciente ON atenciones_medicas(paciente_id);
        CREATE INDEX IF NOT EXISTS idx_atenciones_fecha ON atenciones_medicas(fecha_atencion);
        CREATE INDEX IF NOT EXISTS idx_atenciones_estado ON atenciones_medicas(estado);
        """

        # 3. TABLA AGENDA/CITAS
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
            motivo VARCHAR(200),
            estado_cita VARCHAR(20) DEFAULT 'disponible' CHECK (estado_cita IN ('disponible', 'reservada', 'confirmada', 'completada', 'cancelada')),
            notas TEXT,
            recordatorio_enviado BOOLEAN DEFAULT FALSE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Índices para agenda
        CREATE INDEX IF NOT EXISTS idx_agenda_profesional ON agenda_citas(profesional_id);
        CREATE INDEX IF NOT EXISTS idx_agenda_paciente ON agenda_citas(paciente_id);
        CREATE INDEX IF NOT EXISTS idx_agenda_fecha ON agenda_citas(fecha);
        CREATE INDEX IF NOT EXISTS idx_agenda_disponible ON agenda_citas(disponible);
        """

        # 4. TABLA HORARIOS DISPONIBLES
        horarios_sql = """
        CREATE TABLE IF NOT EXISTS horarios_disponibles (
            id SERIAL PRIMARY KEY,
            profesional_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            dia_semana VARCHAR(20) NOT NULL CHECK (dia_semana IN ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo')),
            hora_inicio TIME NOT NULL,
            hora_fin TIME NOT NULL,
            duracion_cita INTEGER DEFAULT 30, -- minutos
            estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo'))
        );
        
        -- Índices para horarios
        CREATE INDEX IF NOT EXISTS idx_horarios_profesional ON horarios_disponibles(profesional_id);
        CREATE INDEX IF NOT EXISTS idx_horarios_dia ON horarios_disponibles(dia_semana);
        """

        # 5. TABLA ESPECIALIDADES
        especialidades_sql = """
        CREATE TABLE IF NOT EXISTS especialidades (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) UNIQUE NOT NULL,
            descripcion TEXT,
            icono VARCHAR(50),
            estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo'))
        );
        
        -- Índice para especialidades
        CREATE INDEX IF NOT EXISTS idx_especialidades_nombre ON especialidades(nombre);
        """

        # 6. TABLA ARCHIVOS MÉDICOS
        archivos_sql = """
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
        
        -- Índices para archivos
        CREATE INDEX IF NOT EXISTS idx_archivos_paciente ON archivos_medicos(paciente_id);
        CREATE INDEX IF NOT EXISTS idx_archivos_profesional ON archivos_medicos(profesional_id);
        CREATE INDEX IF NOT EXISTS idx_archivos_atencion ON archivos_medicos(atencion_id);
        """

        # 7. TABLA PACIENTES_PROFESIONAL (relación)
        pacientes_profesional_sql = """
        CREATE TABLE IF NOT EXISTS pacientes_profesional (
            id SERIAL PRIMARY KEY,
            profesional_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            paciente_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            fecha_primera_atencion DATE,
            total_atenciones INTEGER DEFAULT 0,
            ultima_atencion DATE,
            notas_generales TEXT,
            estado_relacion VARCHAR(20) DEFAULT 'activo' CHECK (estado_relacion IN ('activo', 'inactivo')),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Evitar duplicados
            UNIQUE(profesional_id, paciente_id)
        );
        
        -- Índices para relación pacientes-profesional
        CREATE INDEX IF NOT EXISTS idx_pacientes_prof_profesional ON pacientes_profesional(profesional_id);
        CREATE INDEX IF NOT EXISTS idx_pacientes_prof_paciente ON pacientes_profesional(paciente_id);
        """

        try:
            # Ejecutar todas las consultas
            logger.info("📋 Creando tabla 'usuarios'...")
            self.cursor.execute(usuarios_sql)

            logger.info("📋 Creando tabla 'atenciones_medicas'...")
            self.cursor.execute(atenciones_sql)

            logger.info("📋 Creando tabla 'agenda_citas'...")
            self.cursor.execute(agenda_sql)

            logger.info("📋 Creando tabla 'horarios_disponibles'...")
            self.cursor.execute(horarios_sql)

            logger.info("📋 Creando tabla 'especialidades'...")
            self.cursor.execute(especialidades_sql)

            logger.info("📋 Creando tabla 'archivos_medicos'...")
            self.cursor.execute(archivos_sql)

            logger.info("📋 Creando tabla 'pacientes_profesional'...")
            self.cursor.execute(pacientes_profesional_sql)

            # Confirmar cambios
            self.conn.commit()
            logger.info("✅ ¡TODAS LAS TABLAS CREADAS EXITOSAMENTE!")
            return True

        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")
            self.conn.rollback()
            return False

    def insert_sample_data(self):
        """Insertar datos de ejemplo completos"""
        logger.info("📝 Insertando datos de ejemplo...")

        try:
            # Hash para contraseña "password123"
            password_hash = bcrypt.hashpw(
                "password123".encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            # 1. INSERTAR ESPECIALIDADES
            especialidades_data = [
                (
                    "Medicina General",
                    "Atención médica integral y preventiva",
                    "stethoscope",
                ),
                (
                    "Cardiología",
                    "Especialidad en enfermedades del corazón y sistema cardiovascular",
                    "heart",
                ),
                (
                    "Traumatología",
                    "Especialidad en sistema músculo-esquelético",
                    "bone",
                ),
                ("Pediatría", "Especialidad en atención médica infantil", "baby"),
                ("Ginecología", "Especialidad en salud femenina", "female"),
                ("Dermatología", "Especialidad en enfermedades de la piel", "skin"),
            ]

            for esp in especialidades_data:
                self.cursor.execute(
                    """
                    INSERT INTO especialidades (nombre, descripcion, icono) 
                    VALUES (%s, %s, %s) ON CONFLICT (nombre) DO NOTHING
                """,
                    esp,
                )

            logger.info("✅ Especialidades insertadas")

            # 2. INSERTAR USUARIOS (PROFESIONALES Y PACIENTES)
            usuarios_data = [
                # Profesionales
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
                    "nombre": "Ana",
                    "apellido": "Rodríguez",
                    "email": "ana.rodriguez@medconnect.com",
                    "password_hash": password_hash,
                    "tipo_usuario": "profesional",
                    "telefono": "+56912345678",
                    "ciudad": "Santiago",
                    "especialidad": "Cardiología",
                    "numero_colegiado": "CARD-002",
                    "hospital": "Clínica Las Condes",
                    "anos_experiencia": 15,
                },
                # Pacientes
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
                {
                    "nombre": "Carlos",
                    "apellido": "Mendoza",
                    "email": "carlos.mendoza@test.com",
                    "password_hash": password_hash,
                    "tipo_usuario": "paciente",
                    "telefono": "+56998877665",
                    "ciudad": "Valparaíso",
                    "fecha_nacimiento": "1978-03-10",
                    "genero": "Masculino",
                    "direccion": "Av. Brasil 789, Valparaíso",
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

            # 3. INSERTAR HORARIOS DISPONIBLES PARA PROFESIONALES
            horarios_data = [
                # Diego Castro (ID: 1)
                (1, "Lunes", "09:00", "18:00", 30),
                (1, "Martes", "09:00", "18:00", 30),
                (1, "Miércoles", "09:00", "18:00", 30),
                (1, "Jueves", "09:00", "18:00", 30),
                (1, "Viernes", "09:00", "17:00", 30),
                # Ana Rodríguez (ID: 2)
                (2, "Lunes", "08:00", "17:00", 45),
                (2, "Martes", "08:00", "17:00", 45),
                (2, "Jueves", "08:00", "17:00", 45),
                (2, "Viernes", "08:00", "16:00", 45),
            ]

            for horario in horarios_data:
                self.cursor.execute(
                    """
                    INSERT INTO horarios_disponibles (profesional_id, dia_semana, hora_inicio, hora_fin, duracion_cita)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    horario,
                )

            logger.info("✅ Horarios disponibles insertados")

            # 4. INSERTAR CITAS DE EJEMPLO
            agenda_data = [
                {
                    "profesional_id": 1,
                    "paciente_id": 3,
                    "fecha": "2025-09-01",
                    "hora_inicio": "10:00",
                    "hora_fin": "10:30",
                    "disponible": False,
                    "tipo_cita": "Control",
                    "motivo": "Control mensual",
                    "estado_cita": "confirmada",
                    "notas": "Paciente regular",
                },
                {
                    "profesional_id": 1,
                    "paciente_id": None,
                    "fecha": "2025-09-01",
                    "hora_inicio": "11:00",
                    "hora_fin": "11:30",
                    "disponible": True,
                    "tipo_cita": "Consulta",
                    "estado_cita": "disponible",
                },
                {
                    "profesional_id": 2,
                    "paciente_id": 4,
                    "fecha": "2025-09-02",
                    "hora_inicio": "14:00",
                    "hora_fin": "14:45",
                    "disponible": False,
                    "tipo_cita": "Primera Vez",
                    "motivo": "Consulta cardiológica",
                    "estado_cita": "programada",
                    "notas": "Derivado por médico general",
                },
            ]

            for cita in agenda_data:
                columns = ", ".join(cita.keys())
                placeholders = ", ".join(["%s"] * len(cita))
                query = f"INSERT INTO agenda_citas ({columns}) VALUES ({placeholders})"
                self.cursor.execute(query, list(cita.values()))

            logger.info("✅ Citas de ejemplo insertadas")

            # 5. INSERTAR ATENCIONES DE EJEMPLO
            atenciones_data = [
                {
                    "atencion_id": "ATN_20250830_001",
                    "profesional_id": 1,
                    "paciente_id": 3,
                    "profesional_nombre": "Diego Castro",
                    "paciente_nombre": "Juan Pérez",
                    "fecha_atencion": "2025-08-30",
                    "hora_inicio": "10:00",
                    "hora_fin": "10:30",
                    "tipo_atencion": "Control",
                    "motivo_consulta": "Control rutinario mensual",
                    "diagnostico": "Paciente en buen estado general",
                    "tratamiento": "Continuar con medicación actual",
                    "observaciones": "Próximo control en 1 mes",
                    "estado": "completada",
                }
            ]

            for atencion in atenciones_data:
                columns = ", ".join(atencion.keys())
                placeholders = ", ".join(["%s"] * len(atencion))
                query = f"INSERT INTO atenciones_medicas ({columns}) VALUES ({placeholders})"
                self.cursor.execute(query, list(atencion.values()))

            logger.info("✅ Atenciones de ejemplo insertadas")

            # Confirmar todos los cambios
            self.conn.commit()
            logger.info("✅ ¡TODOS LOS DATOS DE EJEMPLO INSERTADOS!")
            return True

        except Exception as e:
            logger.error(f"❌ Error insertando datos: {e}")
            self.conn.rollback()
            return False

    def verify_tables(self):
        """Verificar que todas las tablas se crearon correctamente"""
        logger.info("🔍 Verificando tablas creadas...")

        try:
            # Obtener lista de tablas
            self.cursor.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """
            )

            tables = [row["table_name"] for row in self.cursor.fetchall()]
            expected_tables = [
                "usuarios",
                "atenciones_medicas",
                "agenda_citas",
                "horarios_disponibles",
                "especialidades",
                "archivos_medicos",
                "pacientes_profesional",
            ]

            logger.info(f"📊 Tablas encontradas: {', '.join(tables)}")

            # Verificar cada tabla esperada
            for table in expected_tables:
                if table in tables:
                    # Contar registros
                    self.cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    count = self.cursor.fetchone()["count"]
                    logger.info(f"✅ {table}: {count} registros")
                else:
                    logger.error(f"❌ Tabla faltante: {table}")

            # Verificar usuarios específicos
            self.cursor.execute(
                "SELECT email, tipo_usuario FROM usuarios ORDER BY tipo_usuario, email"
            )
            users = self.cursor.fetchall()

            logger.info("👥 Usuarios creados:")
            for user in users:
                logger.info(f"  - {user['email']} ({user['tipo_usuario']})")

            return True

        except Exception as e:
            logger.error(f"❌ Error verificando tablas: {e}")
            return False

    def close_connection(self):
        """Cerrar conexión"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("🔒 Conexión cerrada")


def main():
    """Función principal - EJECUTA TODO AUTOMÁTICAMENTE"""
    logger.info("🚀 CREADOR AUTOMÁTICO DE TABLAS POSTGRESQL - MEDCONNECT")
    logger.info("=" * 60)

    creator = AutoTableCreator()

    try:
        # Paso 1: Conectar
        if not creator.connect_to_postgresql():
            logger.error("❌ No se pudo conectar a PostgreSQL")
            return False

        # Paso 2: Crear todas las tablas
        if not creator.create_all_tables():
            logger.error("❌ No se pudieron crear las tablas")
            return False

        # Paso 3: Insertar datos de ejemplo
        if not creator.insert_sample_data():
            logger.error("❌ No se pudieron insertar los datos")
            return False

        # Paso 4: Verificar todo
        if not creator.verify_tables():
            logger.error("❌ Las verificaciones fallaron")
            return False

        logger.info("🎉 ¡MIGRACIÓN AUTOMÁTICA COMPLETADA EXITOSAMENTE!")
        logger.info("=" * 60)
        logger.info("✅ Todas las tablas creadas")
        logger.info("✅ Datos de ejemplo insertados")
        logger.info("✅ Sistema listo para usar")
        logger.info("")
        logger.info("👥 USUARIOS DISPONIBLES PARA LOGIN:")
        logger.info("   📧 diego.castro.lagos@gmail.com (profesional) - password123")
        logger.info("   📧 ana.rodriguez@medconnect.com (profesional) - password123")
        logger.info("   📧 paciente@test.com (paciente) - password123")
        logger.info("   📧 maria.gonzalez@test.com (paciente) - password123")
        logger.info("   📧 carlos.mendoza@test.com (paciente) - password123")
        logger.info("")
        logger.info("🔄 PRÓXIMO PASO: Actualizar app.py para usar PostgreSQL")

        return True

    except Exception as e:
        logger.error(f"❌ Error durante la migración: {e}")
        return False

    finally:
        creator.close_connection()


if __name__ == "__main__":
    main()
