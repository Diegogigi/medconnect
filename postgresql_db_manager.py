#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Manager para PostgreSQL - Reemplazo de Google Sheets
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgreSQLDBManager:
    def __init__(self):
        """Inicializar el gestor de base de datos PostgreSQL"""
        self.conn = None
        self.cursor = None
        self.connected = False

        # Intentar conectar
        self.connect()

    def connect(self):
        """Conectar a PostgreSQL"""
        try:
            # Debug: Mostrar todas las variables de entorno relacionadas con DB
            logger.info("🔍 Verificando variables de entorno de base de datos...")
            database_url = os.environ.get("DATABASE_URL")
            pghost = os.environ.get("PGHOST")
            pgdatabase = os.environ.get("PGDATABASE")
            pguser = os.environ.get("PGUSER")
            pgpassword = os.environ.get("PGPASSWORD")
            pgport = os.environ.get("PGPORT")

            logger.info(f"📋 Variables encontradas:")
            logger.info(
                f"   DATABASE_URL: {'✅ Configurada' if database_url else '❌ No configurada'}"
            )
            logger.info(f"   PGHOST: {pghost or 'No configurado'}")
            logger.info(f"   PGDATABASE: {pgdatabase or 'No configurado'}")
            logger.info(f"   PGUSER: {pguser or 'No configurado'}")
            logger.info(
                f"   PGPASSWORD: {'✅ Configurada' if pgpassword else '❌ No configurada'}"
            )
            logger.info(f"   PGPORT: {pgport or 'No configurado'}")

            if database_url:
                logger.info("🔗 Conectando usando DATABASE_URL de Railway...")
                logger.info(
                    f"   URL: {database_url[:50]}..."
                    if len(database_url) > 50
                    else f"   URL: {database_url}"
                )
                self.conn = psycopg2.connect(database_url)
            else:
                # Fallback para desarrollo local
                logger.info("🔗 Conectando usando variables individuales...")
                self.conn = psycopg2.connect(
                    host=pghost or "localhost",
                    database=pgdatabase or "medconnect",
                    user=pguser or "postgres",
                    password=pgpassword or "",
                    port=pgport or "5432",
                )

            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            self.connected = True
            logger.info("✅ PostgreSQL DB Manager conectado exitosamente")

        except Exception as e:
            logger.error(f"❌ Error conectando a PostgreSQL: {e}")
            self.connected = False
            # En Railway, si no hay DATABASE_URL, no intentar localhost
            if not database_url:
                logger.warning("⚠️ No se encontró DATABASE_URL - modo fallback activado")
                logger.warning(
                    "🔧 Verifica que DATABASE_URL esté configurada en Railway"
                )

    def is_connected(self) -> bool:
        """Verificar si está conectado"""
        return self.connected and self.conn is not None

    # ==================== MÉTODOS PARA ATENCIONES MÉDICAS ====================

    def get_atenciones(self, profesional_id: Optional[int] = None) -> List[Dict]:
        """Obtener atenciones médicas"""
        if not self.connected:
            return self._get_fallback_atenciones()

        try:
            if profesional_id:
                query = """
                SELECT a.*, 
                       p.nombre as paciente_nombre, p.apellido as paciente_apellido,
                       pr.nombre as profesional_nombre, pr.apellido as profesional_apellido
                FROM atenciones_medicas a
                LEFT JOIN usuarios p ON a.paciente_id = p.id
                LEFT JOIN usuarios pr ON a.profesional_id = pr.id
                WHERE a.profesional_id = %s
                ORDER BY a.fecha_atencion DESC, a.hora_inicio DESC
                """
                self.cursor.execute(query, (profesional_id,))
            else:
                query = """
                SELECT a.*, 
                       p.nombre as paciente_nombre, p.apellido as paciente_apellido,
                       pr.nombre as profesional_nombre, pr.apellido as profesional_apellido
                FROM atenciones_medicas a
                LEFT JOIN usuarios p ON a.paciente_id = p.id
                LEFT JOIN usuarios pr ON a.profesional_id = pr.id
                ORDER BY a.fecha_atencion DESC, a.hora_inicio DESC
                """
                self.cursor.execute(query)

            results = self.cursor.fetchall()
            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"❌ Error obteniendo atenciones: {e}")
            return self._get_fallback_atenciones()

    def create_atencion(self, atencion_data: Dict) -> bool:
        """Crear nueva atención médica"""
        if not self.connected:
            return False

        try:
            query = """
            INSERT INTO atenciones_medicas 
            (profesional_id, paciente_id, fecha_atencion, hora_inicio, hora_fin,
             tipo_atencion, motivo_consulta, diagnostico, tratamiento, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """

            self.cursor.execute(
                query,
                (
                    atencion_data["profesional_id"],
                    atencion_data["paciente_id"],
                    atencion_data["fecha_atencion"],
                    atencion_data["hora_inicio"],
                    atencion_data.get("hora_fin"),
                    atencion_data["tipo_atencion"],
                    atencion_data.get("motivo_consulta"),
                    atencion_data.get("diagnostico"),
                    atencion_data.get("tratamiento"),
                    atencion_data.get("observaciones"),
                ),
            )

            atencion_id = self.cursor.fetchone()["id"]
            self.conn.commit()

            logger.info(f"✅ Atención creada exitosamente (ID: {atencion_id})")
            return True

        except Exception as e:
            logger.error(f"❌ Error creando atención: {e}")
            self.conn.rollback()
            return False

    # ==================== MÉTODOS PARA PACIENTES ====================

    def get_pacientes(self, profesional_id: Optional[int] = None) -> List[Dict]:
        """Obtener lista de pacientes"""
        if not self.connected:
            return self._get_fallback_pacientes()

        try:
            if profesional_id:
                # Pacientes que han tenido atenciones con este profesional
                query = """
                SELECT DISTINCT u.id, u.nombre, u.apellido, u.email, u.telefono,
                       u.fecha_nacimiento, u.genero, u.direccion, u.ciudad, u.estado,
                       COUNT(a.id) as total_atenciones,
                       MAX(a.fecha_atencion) as ultima_atencion
                FROM usuarios u
                LEFT JOIN atenciones_medicas a ON u.id = a.paciente_id AND a.profesional_id = %s
                WHERE u.tipo_usuario = 'paciente' AND u.estado = 'activo'
                GROUP BY u.id, u.nombre, u.apellido, u.email, u.telefono, 
                         u.fecha_nacimiento, u.genero, u.direccion, u.ciudad, u.estado
                ORDER BY u.apellido, u.nombre
                """
                self.cursor.execute(query, (profesional_id,))
            else:
                query = """
                SELECT id, nombre, apellido, email, telefono, fecha_nacimiento,
                       genero, direccion, ciudad, estado
                FROM usuarios 
                WHERE tipo_usuario = 'paciente' AND estado = 'activo'
                ORDER BY apellido, nombre
                """
                self.cursor.execute(query)

            results = self.cursor.fetchall()
            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"❌ Error obteniendo pacientes: {e}")
            return self._get_fallback_pacientes()

    def get_paciente_by_id(self, paciente_id: int) -> Optional[Dict]:
        """Obtener paciente por ID"""
        if not self.connected:
            fallback_pacientes = self._get_fallback_pacientes()
            return next((p for p in fallback_pacientes if p["id"] == paciente_id), None)

        try:
            query = """
            SELECT id, nombre, apellido, email, telefono, fecha_nacimiento,
                   genero, direccion, ciudad, estado, fecha_registro
            FROM usuarios 
            WHERE id = %s AND tipo_usuario = 'paciente' AND estado = 'activo'
            """

            self.cursor.execute(query, (paciente_id,))
            result = self.cursor.fetchone()

            return dict(result) if result else None

        except Exception as e:
            logger.error(f"❌ Error obteniendo paciente por ID: {e}")
            return None

    # ==================== MÉTODOS PARA AGENDA/CITAS ====================

    def get_agenda(
        self, profesional_id: Optional[int] = None, fecha: Optional[str] = None
    ) -> List[Dict]:
        """Obtener agenda/citas"""
        if not self.connected:
            return self._get_fallback_agenda()

        try:
            query = """
            SELECT a.*, 
                   p.nombre as paciente_nombre, p.apellido as paciente_apellido,
                   pr.nombre as profesional_nombre, pr.apellido as profesional_apellido
            FROM agenda_citas a
            LEFT JOIN usuarios p ON a.paciente_id = p.id
            LEFT JOIN usuarios pr ON a.profesional_id = pr.id
            WHERE 1=1
            """
            params = []

            if profesional_id:
                query += " AND a.profesional_id = %s"
                params.append(profesional_id)

            if fecha:
                query += " AND a.fecha = %s"
                params.append(fecha)

            query += " ORDER BY a.fecha, a.hora_inicio"

            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"❌ Error obteniendo agenda: {e}")
            return self._get_fallback_agenda()

    def create_cita(self, cita_data: Dict) -> bool:
        """Crear nueva cita"""
        if not self.connected:
            return False

        try:
            query = """
            INSERT INTO agenda_citas 
            (profesional_id, paciente_id, fecha, hora_inicio, hora_fin,
             tipo_cita, notas, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """

            self.cursor.execute(
                query,
                (
                    cita_data["profesional_id"],
                    cita_data.get("paciente_id"),
                    cita_data["fecha"],
                    cita_data["hora_inicio"],
                    cita_data["hora_fin"],
                    cita_data.get("tipo_cita"),
                    cita_data.get("notas"),
                    cita_data.get("estado", "programada"),
                ),
            )

            cita_id = self.cursor.fetchone()["id"]
            self.conn.commit()

            logger.info(f"✅ Cita creada exitosamente (ID: {cita_id})")
            return True

        except Exception as e:
            logger.error(f"❌ Error creando cita: {e}")
            self.conn.rollback()
            return False

    # ==================== MÉTODOS PARA USUARIOS ====================

    def get_usuarios(self, tipo_usuario: Optional[str] = None) -> List[Dict]:
        """Obtener usuarios"""
        if not self.connected:
            return self._get_fallback_usuarios()

        try:
            if tipo_usuario:
                query = """
                SELECT id, nombre, apellido, email, telefono, ciudad, estado,
                       tipo_usuario, especialidad, numero_colegiado, hospital
                FROM usuarios 
                WHERE tipo_usuario = %s AND estado = 'activo'
                ORDER BY apellido, nombre
                """
                self.cursor.execute(query, (tipo_usuario,))
            else:
                query = """
                SELECT id, nombre, apellido, email, telefono, ciudad, estado,
                       tipo_usuario, especialidad, numero_colegiado, hospital
                FROM usuarios 
                WHERE estado = 'activo'
                ORDER BY tipo_usuario, apellido, nombre
                """
                self.cursor.execute(query)

            results = self.cursor.fetchall()
            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"❌ Error obteniendo usuarios: {e}")
            return self._get_fallback_usuarios()

    # ==================== MÉTODOS DE FALLBACK ====================

    def _get_fallback_atenciones(self) -> List[Dict]:
        """Datos de fallback para atenciones"""
        return [
            {
                "id": 1,
                "profesional_id": 1,
                "paciente_id": 2,
                "fecha_atencion": "2025-08-30",
                "hora_inicio": "10:00",
                "hora_fin": "10:30",
                "tipo_atencion": "Consulta General",
                "motivo_consulta": "Control rutinario",
                "diagnostico": "Paciente en buen estado general",
                "tratamiento": "Continuar con medicación actual",
                "observaciones": "Próximo control en 3 meses",
                "estado": "completada",
                "paciente_nombre": "Juan",
                "paciente_apellido": "Pérez",
                "profesional_nombre": "Diego",
                "profesional_apellido": "Castro",
            },
            {
                "id": 2,
                "profesional_id": 1,
                "paciente_id": 3,
                "fecha_atencion": "2025-08-31",
                "hora_inicio": "14:00",
                "hora_fin": "14:45",
                "tipo_atencion": "Consulta Especializada",
                "motivo_consulta": "Seguimiento tratamiento",
                "diagnostico": "Evolución favorable",
                "tratamiento": "Ajuste de medicación",
                "observaciones": "Cita de seguimiento programada",
                "estado": "programada",
                "paciente_nombre": "María",
                "paciente_apellido": "González",
                "profesional_nombre": "Diego",
                "profesional_apellido": "Castro",
            },
        ]

    def _get_fallback_pacientes(self) -> List[Dict]:
        """Datos de fallback para pacientes"""
        return [
            {
                "id": 2,
                "nombre": "Juan",
                "apellido": "Pérez",
                "email": "paciente@test.com",
                "telefono": "+56912345678",
                "fecha_nacimiento": "1990-05-15",
                "genero": "Masculino",
                "direccion": "Av. Providencia 123, Santiago",
                "ciudad": "Santiago",
                "estado": "activo",
                "total_atenciones": 5,
                "ultima_atencion": "2025-08-30",
            },
            {
                "id": 3,
                "nombre": "María",
                "apellido": "González",
                "email": "maria.gonzalez@test.com",
                "telefono": "+56987654321",
                "fecha_nacimiento": "1985-12-20",
                "genero": "Femenino",
                "direccion": "Calle Las Condes 456, Santiago",
                "ciudad": "Santiago",
                "estado": "activo",
                "total_atenciones": 3,
                "ultima_atencion": "2025-08-25",
            },
        ]

    def _get_fallback_agenda(self) -> List[Dict]:
        """Datos de fallback para agenda"""
        return [
            {
                "id": 1,
                "profesional_id": 1,
                "paciente_id": None,
                "fecha": "2025-08-31",
                "hora_inicio": "09:00",
                "hora_fin": "09:30",
                "disponible": True,
                "tipo_cita": "Consulta General",
                "notas": "Horario disponible",
                "estado": "disponible",
                "profesional_nombre": "Diego",
                "profesional_apellido": "Castro",
            },
            {
                "id": 2,
                "profesional_id": 1,
                "paciente_id": 2,
                "fecha": "2025-09-01",
                "hora_inicio": "10:00",
                "hora_fin": "10:30",
                "disponible": False,
                "tipo_cita": "Control",
                "notas": "Control mensual",
                "estado": "confirmada",
                "paciente_nombre": "Juan",
                "paciente_apellido": "Pérez",
                "profesional_nombre": "Diego",
                "profesional_apellido": "Castro",
            },
        ]

    def _get_fallback_usuarios(self) -> List[Dict]:
        """Datos de fallback para usuarios"""
        return [
            {
                "id": 1,
                "nombre": "Diego",
                "apellido": "Castro",
                "email": "diego.castro.lagos@gmail.com",
                "telefono": "+56979712175",
                "ciudad": "Talcahuano",
                "estado": "activo",
                "tipo_usuario": "profesional",
                "especialidad": "Medicina General",
                "numero_colegiado": "MED-001",
                "hospital": "Hospital Regional",
            },
            {
                "id": 2,
                "nombre": "Juan",
                "apellido": "Pérez",
                "email": "paciente@test.com",
                "telefono": "+56912345678",
                "ciudad": "Santiago",
                "estado": "activo",
                "tipo_usuario": "paciente",
                "especialidad": None,
                "numero_colegiado": None,
                "hospital": None,
            },
        ]

    def close(self):
        """Cerrar conexión"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("🔒 Conexión PostgreSQL DB Manager cerrada")

    # No crear instancia global - se crea en app.py cuando sea necesario

    def get_user_by_email(self, email):
        """Obtener usuario por email desde ambas tablas"""
        try:
            # Buscar en tabla profesionales
            self.cursor.execute(
                """
                SELECT id, nombre, apellido, 'profesional' as tipo_usuario
                FROM profesionales 
                WHERE nombre = %s AND apellido = %s
            """,
                (email.split("@")[0], email.split("@")[0]),
            )
            professional = self.cursor.fetchone()

            if professional:
                return {
                    "id": professional[0],
                    "nombre": professional[1],
                    "apellido": professional[2],
                    "email": email,
                    "tipo_usuario": "profesional",
                }

            # Buscar en tabla pacientes_profesional
            self.cursor.execute(
                """
                SELECT paciente_id as id, email, 
                       SPLIT_PART(nombre_completo, ' ', 1) as nombre,
                       SPLIT_PART(nombre_completo, ' ', 2) as apellido,
                       'paciente' as tipo_usuario
                FROM pacientes_profesional 
                WHERE email = %s
            """,
                (email,),
            )
            patient = self.cursor.fetchone()

            if patient:
                return {
                    "id": patient[0],
                    "nombre": patient[1],
                    "apellido": patient[2],
                    "email": patient[3],
                    "tipo_usuario": "paciente",
                }

            return None

        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario por email: {e}")
            return None

    def register_user(self, user_data):
        """Registrar un nuevo usuario en la tabla correspondiente"""
        try:
            tipo_usuario = user_data.get("tipo_usuario", "paciente")

            if tipo_usuario == "paciente":
                return self._register_patient(user_data)
            elif tipo_usuario == "profesional":
                return self._register_professional(user_data)
            else:
                return False, "Tipo de usuario no válido"

        except Exception as e:
            logger.error(f"❌ Error registrando usuario: {e}")
            return False, "Error interno del servidor"

    def _register_patient(self, user_data):
        """Registrar un paciente"""
        try:
            # Generar ID único para paciente
            paciente_id = f"PAC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Insertar en tabla pacientes_profesional
            query = """
                INSERT INTO pacientes_profesional 
                (paciente_id, nombre_completo, rut, edad, fecha_nacimiento, genero, 
                 telefono, email, direccion, antecedentes_medicos, estado_relacion, fecha_registro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Calcular edad si hay fecha de nacimiento
            edad = None
            if user_data.get("fecha_nacimiento"):
                try:
                    fecha_nac = datetime.strptime(
                        user_data["fecha_nacimiento"], "%Y-%m-%d"
                    )
                    edad = (datetime.now() - fecha_nac).days // 365
                except:
                    pass

            values = (
                paciente_id,
                f"{user_data['nombre']} {user_data['apellido']}",
                user_data.get("rut"),
                edad,
                user_data.get("fecha_nacimiento"),
                user_data.get("genero"),
                user_data.get("telefono"),
                user_data["email"],
                user_data.get("direccion"),
                user_data.get("antecedentes_medicos"),
                "activo",
                datetime.now(),
            )

            self.cursor.execute(query, values)
            self.conn.commit()

            logger.info(f"✅ Paciente registrado: {paciente_id}")
            return True, "Paciente registrado exitosamente"

        except Exception as e:
            logger.error(f"❌ Error registrando paciente: {e}")
            self.conn.rollback()
            return False, "Error registrando paciente"

    def _register_professional(self, user_data):
        """Registrar un profesional"""
        try:
            # Insertar en tabla profesionales
            query = """
                INSERT INTO profesionales 
                (nombre, apellido, numero_registro, especialidad, anos_experiencia,
                 calificacion, direccion_consulta, horario_atencion, idiomas, profesion,
                 institucion, estado, disponible, unnamed_21, unnamed_22)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                user_data["nombre"],
                user_data["apellido"],
                user_data.get("numero_registro"),
                user_data.get("especialidad"),
                user_data.get("anos_experiencia"),
                user_data.get("calificacion"),
                user_data.get("direccion_consulta"),
                user_data.get("horario_atencion"),
                user_data.get("idiomas"),
                user_data.get("profesion"),
                user_data.get("institucion"),
                "activo",
                True,
                datetime.now(),
                datetime.now(),
            )

            self.cursor.execute(query, values)
            self.conn.commit()

            logger.info(f"✅ Profesional registrado: {user_data['email']}")
            return True, "Profesional registrado exitosamente"

        except Exception as e:
            logger.error(f"❌ Error registrando profesional: {e}")
            self.conn.rollback()
            return False, "Error registrando profesional"

    def login_user(self, email, password):
        """Iniciar sesión de usuario"""
        try:
            # Buscar en tabla profesionales
            query_prof = "SELECT id, nombre, apellido, especialidad, numero_registro FROM profesionales WHERE nombre = %s AND apellido = %s"
            # Buscar por nombre y apellido (ya que no hay email)
            nombre = email.split("@")[0] if "@" in email else email
            self.cursor.execute(query_prof, (nombre, nombre))
            profesional = self.cursor.fetchone()

            if profesional:
                # Por ahora, aceptar cualquier contraseña para profesionales
                # En producción, deberías verificar hash de contraseña
                return {
                    "id": profesional[0],
                    "nombre": profesional[1],
                    "apellido": profesional[2],
                    "email": email,  # Usar el email original
                    "tipo_usuario": "profesional",
                    "especialidad": profesional[3],
                    "numero_registro": profesional[4],
                }

            # Buscar en tabla pacientes_profesional
            query_pac = "SELECT paciente_id, nombre_completo, email, rut, edad FROM pacientes_profesional WHERE email = %s"
            self.cursor.execute(query_pac, (email,))
            paciente = self.cursor.fetchone()

            if paciente:
                # Por ahora, aceptar cualquier contraseña para pacientes
                # En producción, deberías verificar hash de contraseña
                return {
                    "id": paciente[0],
                    "nombre_completo": paciente[1],
                    "email": paciente[2],
                    "tipo_usuario": "paciente",
                    "rut": paciente[3],
                    "edad": paciente[4],
                }

            return None

        except Exception as e:
            logger.error(f"❌ Error en login: {e}")
            return None

    def email_exists(self, email):
        """Verificar si un email ya existe"""
        try:
            # Verificar en profesionales
            query_prof = "SELECT COUNT(*) FROM profesionales WHERE email = %s"
            # Buscar por nombre y apellido (ya que no hay email)
            nombre = email.split("@")[0] if "@" in email else email
            self.cursor.execute(query_prof, (nombre, nombre))
            count_prof = self.cursor.fetchone()[0]

            # Verificar en pacientes
            query_pac = "SELECT COUNT(*) FROM pacientes_profesional WHERE email = %s"
            self.cursor.execute(query_pac, (email,))
            count_pac = self.cursor.fetchone()[0]

            return count_prof > 0 or count_pac > 0

        except Exception as e:
            logger.error(f"❌ Error verificando email: {e}")
            return False
