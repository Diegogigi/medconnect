#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AuthManager para PostgreSQL - Reemplazo del sistema de Google Sheets
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import logging
import re
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgreSQLAuthManager:
    def __init__(self):
        """Inicializar el gestor de autenticación con PostgreSQL"""
        self.conn = None
        self.cursor = None
        self.connected = False

        # Intentar conectar
        self.connect()

    def connect(self):
        """Conectar a PostgreSQL"""
        try:
            # Railway proporciona DATABASE_URL automáticamente
            database_url = os.environ.get("DATABASE_URL")

            if database_url:
                self.conn = psycopg2.connect(database_url)
            else:
                # Variables individuales como backup
                self.conn = psycopg2.connect(
                    host=os.environ.get("PGHOST", "localhost"),
                    database=os.environ.get("PGDATABASE", "medconnect"),
                    user=os.environ.get("PGUSER", "postgres"),
                    password=os.environ.get("PGPASSWORD", ""),
                    port=os.environ.get("PGPORT", "5432"),
                )

            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            self.connected = True
            logger.info("✅ Conectado a PostgreSQL exitosamente")

        except Exception as e:
            logger.error(f"❌ Error conectando a PostgreSQL: {e}")
            logger.warning("⚠️ Usando sistema de fallback")
            self.connected = False

    def validate_email(self, email: str) -> bool:
        """Validar formato de email"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def validate_password(self, password: str) -> bool:
        """Validar contraseña"""
        return len(password) >= 6

    def hash_password(self, password: str) -> str:
        """Hashear contraseña con bcrypt"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verificar contraseña"""
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except Exception as e:
            logger.error(f"❌ Error verificando contraseña: {e}")
            return False

    def login_user(self, email: str, password: str) -> Tuple[bool, Any]:
        """Autenticar usuario"""
        if not self.connected:
            return self._login_user_fallback(email, password)

        try:
            # Buscar usuario por email
            query = """
            SELECT id, nombre, apellido, email, password_hash, tipo_usuario, 
                   telefono, ciudad, estado, especialidad, numero_colegiado, hospital
            FROM usuarios 
            WHERE email = %s AND estado = 'activo'
            """

            self.cursor.execute(query, (email.lower(),))
            user_record = self.cursor.fetchone()

            if not user_record:
                logger.warning(f"❌ Usuario no encontrado: {email}")
                return False, "Email o contraseña incorrectos"

            # Verificar contraseña
            if not self.verify_password(password, user_record["password_hash"]):
                logger.warning(f"❌ Contraseña incorrecta para: {email}")
                return False, "Email o contraseña incorrectos"

            # Actualizar último acceso
            try:
                update_query = "UPDATE usuarios SET ultimo_acceso = %s WHERE id = %s"
                self.cursor.execute(update_query, (datetime.now(), user_record["id"]))
                self.conn.commit()
            except Exception as e:
                logger.warning(f"⚠️ No se pudo actualizar último acceso: {e}")

            # Preparar datos del usuario
            user_data = {
                "id": user_record["id"],
                "nombre": user_record["nombre"],
                "apellido": user_record["apellido"],
                "email": user_record["email"],
                "tipo_usuario": user_record["tipo_usuario"],
                "telefono": user_record["telefono"],
                "ciudad": user_record["ciudad"],
                "estado": user_record["estado"],
            }

            # Agregar campos específicos para profesionales
            if user_record["tipo_usuario"] == "profesional":
                user_data.update(
                    {
                        "especialidad": user_record["especialidad"],
                        "numero_colegiado": user_record["numero_colegiado"],
                        "hospital": user_record["hospital"],
                    }
                )

            logger.info(f"✅ Login exitoso para: {email}")
            return True, user_data

        except Exception as e:
            logger.error(f"❌ Error en login: {e}")
            return False, "Error interno del servidor"

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Obtener usuario por ID"""
        if not self.connected:
            return self._get_user_fallback(user_id)

        try:
            query = """
            SELECT id, nombre, apellido, email, tipo_usuario, telefono, ciudad, 
                   estado, especialidad, numero_colegiado, hospital, fecha_registro
            FROM usuarios 
            WHERE id = %s AND estado = 'activo'
            """

            self.cursor.execute(query, (user_id,))
            user_record = self.cursor.fetchone()

            if user_record:
                return dict(user_record)

            return None

        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario por ID: {e}")
            return None

    def register_user(self, user_data: Dict) -> Tuple[bool, str]:
        """Registrar nuevo usuario"""
        if not self.connected:
            return False, "Base de datos no disponible"

        try:
            # Validar datos requeridos
            required_fields = [
                "nombre",
                "apellido",
                "email",
                "password",
                "tipo_usuario",
            ]
            for field in required_fields:
                if not user_data.get(field):
                    return False, f"Campo requerido: {field}"

            # Validar email
            if not self.validate_email(user_data["email"]):
                return False, "Formato de email inválido"

            # Validar contraseña
            if not self.validate_password(user_data["password"]):
                return False, "La contraseña debe tener al menos 6 caracteres"

            # Verificar si el usuario ya existe
            self.cursor.execute(
                "SELECT id FROM usuarios WHERE email = %s",
                (user_data["email"].lower(),),
            )
            if self.cursor.fetchone():
                return False, "El email ya está registrado"

            # Hashear contraseña
            password_hash = self.hash_password(user_data["password"])

            # Preparar datos para inserción
            insert_data = {
                "nombre": user_data["nombre"],
                "apellido": user_data["apellido"],
                "email": user_data["email"].lower(),
                "password_hash": password_hash,
                "tipo_usuario": user_data["tipo_usuario"],
                "telefono": user_data.get("telefono"),
                "ciudad": user_data.get("ciudad"),
                "direccion": user_data.get("direccion"),
                "fecha_nacimiento": user_data.get("fecha_nacimiento"),
                "genero": user_data.get("genero"),
            }

            # Campos específicos para profesionales
            if user_data["tipo_usuario"] == "profesional":
                insert_data.update(
                    {
                        "especialidad": user_data.get("especialidad"),
                        "numero_colegiado": user_data.get("numero_colegiado"),
                        "hospital": user_data.get("hospital"),
                        "anos_experiencia": user_data.get("anos_experiencia"),
                    }
                )

            # Construir query dinámicamente
            columns = [k for k, v in insert_data.items() if v is not None]
            values = [insert_data[k] for k in columns]
            placeholders = ", ".join(["%s"] * len(columns))
            columns_str = ", ".join(columns)

            query = f"INSERT INTO usuarios ({columns_str}) VALUES ({placeholders}) RETURNING id"

            self.cursor.execute(query, values)
            user_id = self.cursor.fetchone()["id"]
            self.conn.commit()

            logger.info(
                f"✅ Usuario registrado exitosamente: {user_data['email']} (ID: {user_id})"
            )
            return True, f"Usuario registrado exitosamente con ID: {user_id}"

        except Exception as e:
            logger.error(f"❌ Error registrando usuario: {e}")
            self.conn.rollback()
            return False, "Error interno del servidor"

    def change_password(
        self, user_id: int, old_password: str, new_password: str
    ) -> Tuple[bool, str]:
        """Cambiar contraseña de usuario"""
        if not self.connected:
            return False, "Base de datos no disponible"

        try:
            # Obtener usuario actual
            self.cursor.execute(
                "SELECT password_hash FROM usuarios WHERE id = %s", (user_id,)
            )
            user_record = self.cursor.fetchone()

            if not user_record:
                return False, "Usuario no encontrado"

            # Verificar contraseña actual
            if not self.verify_password(old_password, user_record["password_hash"]):
                return False, "Contraseña actual incorrecta"

            # Validar nueva contraseña
            if not self.validate_password(new_password):
                return False, "La nueva contraseña debe tener al menos 6 caracteres"

            # Hashear nueva contraseña
            new_hash = self.hash_password(new_password)

            # Actualizar contraseña
            update_query = """
            UPDATE usuarios 
            SET password_hash = %s, fecha_cambio_password = %s 
            WHERE id = %s
            """

            self.cursor.execute(update_query, (new_hash, datetime.now(), user_id))
            self.conn.commit()

            logger.info(
                f"✅ Contraseña cambiada exitosamente para usuario ID: {user_id}"
            )
            return True, "Contraseña cambiada exitosamente"

        except Exception as e:
            logger.error(f"❌ Error cambiando contraseña: {e}")
            self.conn.rollback()
            return False, "Error interno del servidor"

    def is_connected(self) -> bool:
        """Verificar si está conectado a la base de datos"""
        return self.connected and self.conn is not None

    def _login_user_fallback(self, email: str, password: str) -> Tuple[bool, Any]:
        """Sistema de login de fallback (igual que antes)"""
        logger.info("🔧 Usando sistema de login de fallback")

        fallback_users = {
            "diego.castro.lagos@gmail.com": {
                "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KqKqKq",
                "id": 1,
                "nombre": "Diego",
                "apellido": "Castro",
                "email": "diego.castro.lagos@gmail.com",
                "tipo_usuario": "profesional",
                "estado": "activo",
                "telefono": "+56979712175",
                "ciudad": "Talcahuano",
            },
            "paciente@test.com": {
                "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KqKqKq",
                "id": 2,
                "nombre": "Juan",
                "apellido": "Pérez",
                "email": "paciente@test.com",
                "tipo_usuario": "paciente",
                "estado": "activo",
                "telefono": "+56912345678",
                "ciudad": "Santiago",
            },
        }

        if email in fallback_users:
            user = fallback_users[email]
            if bcrypt.checkpw(
                password.encode("utf-8"), user["password"].encode("utf-8")
            ):
                return True, {
                    "id": user["id"],
                    "nombre": user["nombre"],
                    "apellido": user["apellido"],
                    "email": user["email"],
                    "tipo_usuario": user["tipo_usuario"],
                    "estado": user["estado"],
                    "telefono": user.get("telefono"),
                    "ciudad": user.get("ciudad"),
                }

        return False, "Email o contraseña incorrectos"

    def _get_user_fallback(self, user_id: int) -> Optional[Dict]:
        """Obtener usuario de fallback por ID"""
        fallback_users = {
            1: {
                "id": 1,
                "nombre": "Diego",
                "apellido": "Castro",
                "email": "diego.castro.lagos@gmail.com",
                "tipo_usuario": "profesional",
                "telefono": "+56979712175",
                "ciudad": "Talcahuano",
                "estado": "activo",
            },
            2: {
                "id": 2,
                "nombre": "Juan",
                "apellido": "Pérez",
                "email": "paciente@test.com",
                "tipo_usuario": "paciente",
                "telefono": "+56912345678",
                "ciudad": "Santiago",
                "estado": "activo",
            },
        }

        return fallback_users.get(user_id)

    def close(self):
        """Cerrar conexión"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("🔒 Conexión PostgreSQL cerrada")


# Instancia global
postgresql_auth = PostgreSQLAuthManager()
