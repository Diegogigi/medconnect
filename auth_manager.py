#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de autenticación para MedConnect
Maneja registro, login y gestión de sesiones con Google Sheets
"""

import os
import gspread
from google.oauth2.service_account import Credentials
import json
import bcrypt
from datetime import datetime
import uuid
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
GOOGLE_SHEETS_ID = "1UvnO2lpZSyv13Hf2eG--kQcTff5BBh7jrZ6taFLJypU"

# Cargar credenciales con debugging detallado
try:
    logger.info("🔍 Iniciando carga de credenciales...")
    
    # Verificar variables de entorno disponibles
    env_vars = {
        "GOOGLE_SERVICE_ACCOUNT_JSON": bool(
            os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        ),
        "GOOGLE_CREDENTIALS_FILE": bool(os.environ.get("GOOGLE_CREDENTIALS_FILE")),
        "GOOGLE_SHEETS_ID": bool(os.environ.get("GOOGLE_SHEETS_ID")),
    }
    logger.info(f"🔧 Variables de entorno disponibles: {env_vars}")
    
    # Intentar cargar desde JSON en variable de entorno
    if os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"):
        logger.info("📄 Cargando credenciales desde GOOGLE_SERVICE_ACCOUNT_JSON...")
        credentials_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")

        # Verificar si es un path en lugar de JSON
        if credentials_json.startswith("./") or credentials_json.startswith("/"):
            logger.info(f"📁 Detectado path de archivo: {credentials_json}")
            if os.path.exists(credentials_json):
                with open(credentials_json, "r") as f:
                    GOOGLE_CREDS = json.load(f)
                logger.info("✅ Credenciales cargadas desde archivo especificado")
            else:
                logger.error(f"❌ Archivo no encontrado: {credentials_json}")
                GOOGLE_CREDS = None
        else:
            # Intentar parsear como JSON
            try:
        GOOGLE_CREDS = json.loads(credentials_json)
        logger.info("✅ Credenciales cargadas desde variable de entorno JSON")
            except json.JSONDecodeError as e:
                logger.error(f"❌ Error parseando JSON: {e}")
                GOOGLE_CREDS = None
    # Intentar cargar desde archivo
    elif os.environ.get("GOOGLE_CREDENTIALS_FILE"):
        logger.info("📁 Cargando credenciales desde archivo...")
        credentials_file = os.environ.get("GOOGLE_CREDENTIALS_FILE")
        with open(credentials_file, "r") as f:
            GOOGLE_CREDS = json.load(f)
        logger.info("✅ Credenciales cargadas desde archivo")
    # Intentar archivos por defecto
    else:
        logger.info("🔍 Buscando archivos de credenciales por defecto...")
        possible_files = [
            "credentials.json",
            "service-account.json",
            "google-credentials.json",
            "medconnect-credentials.json",
        ]
        GOOGLE_CREDS = None
        for file_path in possible_files:
            if os.path.exists(file_path):
                logger.info(f"📁 Encontrado archivo: {file_path}")
                with open(file_path, "r") as f:
                    GOOGLE_CREDS = json.load(f)
                break
        if GOOGLE_CREDS is None:
            logger.error("❌ No se encontraron credenciales de Google")
            
except Exception as e:
    logger.error(f"❌ Error cargando credenciales: {e}")
    GOOGLE_CREDS = None


class AuthManager:
    def __init__(self):
        """Inicializar el gestor de autenticación"""
        self.gc = None
        self.spreadsheet = None
        self.users_sheet = None
        self.use_fallback = False

        try:
            if GOOGLE_CREDS is None:
                logger.warning(
                    "⚠️ Credenciales de Google no disponibles - usando sistema de fallback"
                )
                self.use_fallback = True
                return
                
            # Conectar con Google Sheets
            credentials = Credentials.from_service_account_info(
                GOOGLE_CREDS, scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            self.gc = gspread.authorize(credentials)
            self.spreadsheet = self.gc.open_by_key(GOOGLE_SHEETS_ID)
            
            # Obtener hoja de usuarios
            try:
                self.users_sheet = self.spreadsheet.worksheet("Usuarios")
            except gspread.exceptions.WorksheetNotFound:
                logger.error(
                    "❌ Hoja 'Usuarios' no encontrada. Ejecuta setup_auth_sheets.py primero."
                )
                self.use_fallback = True
                return
                
            logger.info("✅ AuthManager inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando AuthManager: {e}")
            logger.warning("⚠️ Usando sistema de fallback")
            self.use_fallback = True

    def validate_email(self, email):
        """Validar formato de email"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def validate_password(self, password):
        """Validar contraseña"""
        return len(password) >= 6

    def hash_password(self, password):
        """Hashear contraseña"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verificar_si_es_profesional(self, email):
        """Versión de emergencia - Lista hardcodeada para evitar problemas de threading"""
        # Lista hardcodeada temporal para evitar problemas de threading con Google Sheets
        profesionales_conocidos = [
            "diego.castro.lagos@gmail.com",
            "giselle.arratia@gmail.com",
        ]
        
        if email.lower() in profesionales_conocidos:
            logger.info(f"✅ {email} reconocido como profesional (lista de emergencia)")
            return "profesional"
        else:
            logger.info(
                f"ℹ️ {email} no está en lista de emergencia - asumiendo paciente"
            )
            return "paciente"

    def change_password(self, user_id, current_password, new_password):
        """Cambiar contraseña de usuario con validaciones robustas"""
        try:
            logger.info(f"🔒 Iniciando cambio de contraseña para usuario ID: {user_id}")
            
            # Obtener datos del usuario
            all_records = self.users_sheet.get_all_records()
            user_record = None
            row_index = None
            
            for i, record in enumerate(all_records):
                if str(record.get("id", "")) == str(user_id):
                    user_record = record
                    row_index = i + 2  # +2 por header y índice 0
                    break
            
            if not user_record:
                logger.warning(f"⚠️ Usuario no encontrado: ID {user_id}")
                return False, "Usuario no encontrado"
            
            # Verificar contraseña actual
            stored_hash = user_record.get("password_hash", "")
            
            # Verificar contraseña actual
            if not self.verify_password(current_password, stored_hash):
                logger.warning(
                    f"⚠️ Contraseña actual incorrecta para usuario ID: {user_id}"
                )
                return False, "Contraseña actual incorrecta"
            
            # Validar nueva contraseña
            if not self.validate_password(new_password):
                return False, "La nueva contraseña debe tener al menos 6 caracteres"
            
            if new_password == current_password:
                return False, "La nueva contraseña debe ser diferente a la actual"
            
            # Crear hash robusto para nueva contraseña
            new_hash = self.hash_password(new_password)
            if not new_hash:
                logger.error(f"❌ Error creando hash para nueva contraseña")
                return False, "Error procesando nueva contraseña"
            
            # Actualizar contraseña en Google Sheets - VERSIÓN CORREGIDA
            try:
                # Usar formato correcto para Google Sheets API
                cell_range = f"F{row_index}"
                self.users_sheet.update(
                    cell_range, [[new_hash]], value_input_option="RAW"
                )
                logger.info(
                    f"✅ Contraseña actualizada exitosamente para usuario ID: {user_id}"
                )
                
                # Actualizar fecha de último cambio de contraseña
                try:
                    date_range = f"M{row_index}"
                    self.users_sheet.update(
                        date_range,
                        [[datetime.now().isoformat()]],
                        value_input_option="RAW",
                    )
                except Exception as date_error:
                    logger.warning(
                        f"⚠️ No se pudo actualizar fecha de cambio: {date_error}"
                    )
                
                return True, "Contraseña cambiada exitosamente"
                
            except Exception as e:
                logger.error(f"❌ Error actualizando contraseña en Google Sheets: {e}")
                return False, "Error actualizando contraseña. Intente más tarde"
                
        except Exception as e:
            logger.error(f"❌ Error general en cambio de contraseña: {e}")
            return False, "Error interno. Contacte al administrador"

    def is_valid_bcrypt_hash(self, hash_string):
        """Verificar si un string es un hash bcrypt válido - VERSIÓN MEJORADA"""
        try:
            if not hash_string:
                return False
            
            # Un hash bcrypt típico tiene 60 caracteres y empieza con $2
            if len(hash_string) < 50:  # Muy corto para ser un hash bcrypt
                return False
            
            # Verificar formato bcrypt típico ($2a$, $2b$, $2y$, etc.)
            if hash_string.startswith("$2") and "$" in hash_string[3:]:
                return True
            
            # Si no sigue el formato estándar de bcrypt, es sospechoso
            if not hash_string.startswith("$"):
                return False
            
            # Verificar longitud mínima para hashes válidos
            if len(hash_string) >= 50:
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Error validando hash bcrypt: {e}")
            return False

    def verify_password(self, password, hashed):
        """Verificar contraseña con manejo robusto de 'Invalid salt'"""
        try:
            # Validaciones previas
            if not password or not hashed:
                logger.warning("⚠️ Contraseña o hash vacío")
                return False
                
            # Verificar que el hash es válido
            if not self.is_valid_bcrypt_hash(hashed):
                logger.error(
                    f"❌ Hash bcrypt inválido/corrupto detectado: {hashed[:20]}..."
                )
                return False
            
            # Intentar verificación normal
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
            
        except ValueError as e:
            if "Invalid salt" in str(e):
                logger.error(
                    f"❌ Error 'Invalid salt' detectado - Hash corrupto: {hashed[:20]}..."
                )
                return False
            else:
                logger.error(f"❌ Error de valor en verificación: {e}")
                return False
        except Exception as e:
            logger.error(f"❌ Error general en verificación de contraseña: {e}")
            return False

    def email_exists(self, email):
        """Verificar si el email ya existe"""
        try:
            all_records = self.users_sheet.get_all_records()
            for record in all_records:
                if record.get("email", "").lower() == email.lower():
                    return True
            return False
        except Exception as e:
            logger.error(f"❌ Error verificando email: {e}")
            return False

    def get_next_user_id(self):
        """Obtener el siguiente ID de usuario"""
        try:
            all_records = self.users_sheet.get_all_records()
            if all_records:
                max_id = max(
                    [
                        int(record.get("id", 0))
                        for record in all_records
                        if record.get("id")
                    ]
                )
                return max_id + 1
            return 1
        except Exception as e:
            logger.error(f"❌ Error obteniendo siguiente ID: {e}")
            return 1

    def register_user(self, user_data):
        """Registrar un nuevo usuario"""
        try:
            # Validar datos
            if not self.validate_email(user_data["email"]):
                return False, "Email inválido"
            
            if not self.validate_password(user_data["password"]):
                return False, "Contraseña debe tener al menos 6 caracteres"
            
            if self.email_exists(user_data["email"]):
                return False, "Email ya registrado"
            
            # Generar ID único
            user_id = self.get_next_user_id()
            
            # Hashear contraseña
            hashed_password = self.hash_password(user_data["password"])
            
            # Preparar datos del usuario
            current_time = datetime.now().isoformat()
            user_record = [
                user_id,
                user_data["email"],
                hashed_password,
                user_data["nombre"],
                user_data["apellido"],
                user_data.get("telefono", ""),
                user_data.get("fecha_nacimiento", ""),
                user_data.get("genero", ""),
                user_data.get("direccion", ""),
                user_data.get("ciudad", ""),
                current_time,
                current_time,
                user_data.get("tipo_usuario", "paciente"),
                "false",  # verificado
                "activo",  # estado
            ]
            
            # Agregar usuario
            self.users_sheet.append_row(user_record)
            
            # Si es profesional, agregar a hoja de profesionales
            if user_data.get("tipo_usuario") == "profesional":
                self._add_professional_to_sheet(user_id, user_data)
            
            logger.info(f"✅ Usuario registrado exitosamente: {user_data['email']}")
            return True, "Usuario registrado exitosamente"
            
        except Exception as e:
            logger.error(f"❌ Error registrando usuario: {e}")
            return False, "Error interno del servidor"

    def _add_professional_to_sheet(self, user_id, user_data):
        """Agregar profesional a la hoja de profesionales"""
        try:
            # Obtener o crear hoja de profesionales
            try:
                prof_sheet = self.spreadsheet.worksheet("Profesionales")
            except gspread.exceptions.WorksheetNotFound:
                prof_sheet = self.spreadsheet.add_worksheet(
                    title="Profesionales", rows=1000, cols=20
                )
                # Agregar encabezados
                headers = [
                    "ID",
                    "Email",
                    "Nombre",
                    "Apellido",
                    "Telefono",
                    "Numero_Registro",
                    "Especialidad",
                    "Anos_Experiencia",
                    "Calificacion",
                    "Direccion_Consulta",
                    "Horario_Atencion",
                    "Idiomas",
                    "Areas_Especializacion",
                    "Profesion",
                    "Institucion",
                    "Titulo",
                    "Ano_Egreso",
                    "Certificaciones",
                    "Fecha_Registro",
                    "Estado",
                    "Disponible",
                ]
                prof_sheet.append_row(headers)
                logger.info("✅ Hoja 'Profesionales' creada")
            
            # Preparar datos del profesional
            current_time = datetime.now().isoformat()
            prof_record = [
                user_id,
                user_data["email"],
                user_data["nombre"],
                user_data["apellido"],
                user_data.get("telefono", ""),
                user_data.get("numero_registro", ""),
                user_data.get("especialidad", ""),
                user_data.get("anos_experiencia", ""),
                user_data.get("calificacion", ""),
                user_data.get("direccion_consulta", ""),
                user_data.get("horario_atencion", ""),
                user_data.get("idiomas", ""),
                user_data.get("areas_especializacion", ""),
                user_data.get("profesion", ""),
                user_data.get("institucion", ""),
                user_data.get("titulo", ""),
                user_data.get("ano_egreso", ""),
                user_data.get("certificaciones", ""),
                current_time,
                "activo",
                "disponible",
            ]
            
            # Agregar profesional
            prof_sheet.append_row(prof_record)
            logger.info(f"✅ Profesional agregado a la hoja: {user_data['email']}")
            
        except Exception as e:
            logger.error(f"❌ Error agregando profesional: {e}")

    def login_user(self, email, password):
        """Autenticar usuario"""
        if self.use_fallback:
            return self._login_user_fallback(email, password)

        try:
            # Buscar usuario por email
            all_records = self.users_sheet.get_all_records()
            user_record = None
            
            for record in all_records:
                if record.get("email", "").lower() == email.lower():
                    user_record = record
                    break
            
            if not user_record:
                return False, "Email o contraseña incorrectos"
            
            # Verificar contraseña normalmente sin regeneración automática
            stored_hash = user_record.get("password_hash", "")
            
            # Si el hash está vacío o es claramente inválido, rechazar login
            if not stored_hash:
                logger.error(f"❌ Hash de contraseña vacío para {email}")
                return (
                    False,
                    "Error de autenticación. Contacte al administrador para restablecer su contraseña",
                )
            
            # Verificar que el hash tenga un formato mínimamente válido
            if len(stored_hash) < 10:
                logger.error(f"❌ Hash de contraseña demasiado corto para {email}")
                return (
                    False,
                    "Error de autenticación. Contacte al administrador para restablecer su contraseña",
                )
            
            logger.info(f"🔍 Verificando contraseña para {email}...")
            
            # Verificar contraseña normal
            if not self.verify_password(password, stored_hash):
                return False, "Email o contraseña incorrectos"
            
            # Actualizar último acceso
            try:
                row_index = (
                    all_records.index(user_record) + 2
                )  # +2 porque enumerate empieza en 0 y hay header
                self.users_sheet.update(f"L{row_index}", datetime.now().isoformat())
                logger.info(
                    f"✅ Último acceso actualizado: {datetime.now().isoformat()}"
                )
            except Exception as e:
                logger.warning(f"⚠️ No se pudo actualizar último acceso: {e}")
            
            # Determinar tipo de usuario de forma robusta y simple
            raw_tipo_usuario = user_record.get("tipo_usuario", "").strip().lower()
            
            if raw_tipo_usuario in ["profesional", "professional", "doctor", "medico"]:
                tipo_usuario_normalizado = "profesional"
                logger.info(f"✅ Usuario marcado como profesional en hoja Usuarios")
            else:
                # Verificación cruzada simplificada
                logger.info(f"🔍 Verificando en hoja Profesionales...")
                try:
                    tipo_usuario_normalizado = self.verificar_si_es_profesional(email)
                except Exception as e:
                    logger.warning(
                        f"⚠️ Error en verificación cruzada: {e} - Asumiendo paciente"
                    )
                    tipo_usuario_normalizado = "paciente"
            
            # Preparar datos del usuario para la sesión
            user_data = {
                "id": user_record.get("id"),
                "email": user_record.get("email"),
                "nombre": user_record.get("nombre"),
                "apellido": user_record.get("apellido"),
                "telefono": user_record.get("telefono"),
                "fecha_nacimiento": user_record.get("fecha_nacimiento"),
                "genero": user_record.get("genero"),
                "direccion": user_record.get("direccion"),
                "ciudad": user_record.get("ciudad"),
                "fecha_registro": user_record.get("fecha_registro"),
                "tipo_usuario": tipo_usuario_normalizado,  # Usar versión normalizada
                "verificado": user_record.get("verificado"),
                "ultimo_acceso": datetime.now().isoformat(),
            }
            
            # Logging simplificado para evitar problemas de threading
            logger.info(f"✅ Login exitoso: {email}")
            logger.info(
                f"🎯 Tipo usuario final: '{tipo_usuario_normalizado}' → {'professional_dashboard' if tipo_usuario_normalizado == 'profesional' else 'patient_dashboard'}"
            )
            return True, user_data
            
        except Exception as e:
            logger.error(f"❌ Error en login: {e}")
            return False, "Error interno del servidor"

    def _login_user_fallback(self, email, password):
        """Sistema de login de fallback con usuarios predefinidos"""
        logger.info("🔧 Usando sistema de login de fallback")

        # Usuarios de prueba predefinidos
        fallback_users = {
            "diego.castro.lagos@gmail.com": {
                "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KqKqKq",  # "password123"
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
                "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KqKqKq",  # "password123"
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
            # Verificar contraseña (usando bcrypt)
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

    def get_user_by_id(self, user_id):
        """Obtener usuario por ID"""
        if self.use_fallback:
            return self._get_user_fallback(user_id)

        try:
            users_data = self.users_sheet.get_all_records()

            for user in users_data:
                if user.get("id") == user_id:
                    return {
                        "id": user.get("id"),
                        "nombre": user.get("nombre"),
                        "apellido": user.get("apellido"),
                        "email": user.get("email"),
                        "tipo_usuario": user.get("tipo_usuario"),
                        "estado": user.get("estado", "activo"),
                        "telefono": user.get("telefono"),
                        "ciudad": user.get("ciudad"),
                    }
            return None

        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario: {e}")
            return self._get_user_fallback(user_id)

    def _get_user_fallback(self, user_id):
        """Obtener usuario de fallback por ID"""
        fallback_users = {
            1: {
                "id": 1,
                "nombre": "Diego",
                "apellido": "Castro",
                "email": "diego.castro.lagos@gmail.com",
                "tipo_usuario": "profesional",
                "estado": "activo",
                "telefono": "+56979712175",
                "ciudad": "Talcahuano",
            },
            2: {
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

        return fallback_users.get(user_id)

    def update_user_profile(self, user_id, update_data):
        """Actualizar perfil de usuario"""
        try:
            # Buscar usuario
            all_records = self.users_sheet.get_all_records()
            user_index = None
            
            for i, record in enumerate(all_records):
                if str(record.get("id", "")) == str(user_id):
                    user_index = i + 2  # +2 porque enumerate empieza en 0 y hay header
                    break
            
            if user_index is None:
                return False, "Usuario no encontrado"
            
            # Actualizar campos
            updates = []
            for field, value in update_data.items():
                if field in [
                    "nombre",
                    "apellido",
                    "telefono",
                    "fecha_nacimiento",
                    "genero",
                    "direccion",
                    "ciudad",
                ]:
                    col_map = {
                        "nombre": "D",
                        "apellido": "E",
                        "telefono": "F",
                        "fecha_nacimiento": "G",
                        "genero": "H",
                        "direccion": "I",
                        "ciudad": "J",
                    }
                    if field in col_map:
                        cell_address = f"{col_map[field]}{user_index}"
                        self.users_sheet.update(cell_address, value)
                        updates.append(field)
            
            logger.info(f"✅ Perfil actualizado - campos: {updates}")
            return True, "Perfil actualizado correctamente"
            
        except Exception as e:
            logger.error(f"❌ Error actualizando perfil: {e}")
            return False, "Error interno del servidor"

    def get_user_by_email(self, email):
        """Obtener usuario por email"""
        try:
            all_records = self.users_sheet.get_all_records()
            for record in all_records:
                if record.get("email", "").lower() == email.lower():
                    return record
            return None
        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario por email: {e}")
            return None

    def get_user_by_telegram_id(self, telegram_id):
        """Obtener usuario por Telegram ID"""
        try:
            all_records = self.users_sheet.get_all_records()
            for record in all_records:
                if str(record.get("telegram_id", "")) == str(telegram_id):
                    return record
            return None
        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario por Telegram ID: {e}")
            return None

    def link_telegram_account(self, email, telegram_id, telegram_username=""):
        """Vincular cuenta de Telegram"""
        try:
            # Buscar usuario por email
            all_records = self.users_sheet.get_all_records()
            user_index = None
            
            for i, record in enumerate(all_records):
                if record.get("email", "").lower() == email.lower():
                    user_index = i + 2
                    break
            
            if user_index is None:
                return False, "Usuario no encontrado"
            
            # Asegurar que existan las columnas de Telegram
            self._ensure_telegram_columns()
            
            # Actualizar datos de Telegram
            self.users_sheet.update(f"M{user_index}", str(telegram_id))
            self.users_sheet.update(f"N{user_index}", telegram_username)
            
            logger.info(f"✅ Cuenta de Telegram vinculada: {email} -> {telegram_id}")
            return True, "Cuenta de Telegram vinculada correctamente"
            
        except Exception as e:
            logger.error(f"❌ Error vinculando Telegram: {e}")
            return False, "Error interno del servidor"

    def _ensure_telegram_columns(self):
        """Asegurar que existan las columnas de Telegram"""
        try:
            # Obtener headers actuales
            headers = self.users_sheet.row_values(1)
            
            # Verificar si faltan columnas de Telegram
            if "telegram_id" not in headers:
                self.users_sheet.update("M1", "telegram_id")
                logger.info("✅ Columna telegram_id agregada")
            
            if "telegram_username" not in headers:
                self.users_sheet.update("N1", "telegram_username")
                logger.info("✅ Columna telegram_username agregada")
                
        except Exception as e:
            logger.error(f"❌ Error asegurando columnas de Telegram: {e}")

    def _number_to_letter(self, n):
        """Convertir número a letra de columna (A, B, C, ...)"""
        result = ""
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            result = chr(65 + remainder) + result
        return result

    def link_telegram_by_user_id(self, user_id, telegram_id, telegram_username=""):
        """Vincular cuenta de Telegram por user_id"""
        try:
            # Buscar usuario por ID
            all_records = self.users_sheet.get_all_records()
            user_index = None
            
            for i, record in enumerate(all_records):
                if str(record.get("id", "")) == str(user_id):
                    user_index = i + 2
                    break
            
            if user_index is None:
                return False, "Usuario no encontrado"
            
            # Asegurar que existan las columnas de Telegram
            self._ensure_telegram_columns()
            
            # Actualizar datos de Telegram
            self.users_sheet.update(f"M{user_index}", str(telegram_id))
            self.users_sheet.update(f"N{user_index}", telegram_username)
            
            logger.info(
                f"✅ Cuenta de Telegram vinculada por user_id: {user_id} -> {telegram_id}"
            )
            return True, "Cuenta de Telegram vinculada correctamente"
            
        except Exception as e:
            logger.error(f"❌ Error vinculando Telegram por user_id: {e}")
            return False, "Error interno del servidor"

    def update_professional_status(self, user_id, estado=None, disponible=None):
        """Actualizar estado de profesional"""
        try:
            # Obtener hoja de profesionales
            try:
                prof_sheet = self.spreadsheet.worksheet("Profesionales")
            except gspread.exceptions.WorksheetNotFound:
                return False, "Hoja de profesionales no encontrada"
            
            # Buscar profesional
            all_records = prof_sheet.get_all_records()
            prof_index = None
            
            for i, record in enumerate(all_records):
                if str(record.get("ID", "")) == str(user_id):
                    prof_index = i + 2
                    break
            
            if prof_index is None:
                return False, "Profesional no encontrado"
            
            # Actualizar estado
            if estado is not None:
                self.prof_sheet.update(f"T{prof_index}", estado)
                logger.info(f"✅ Estado actualizado: {estado}")
            
            # Actualizar disponibilidad
            if disponible is not None:
                self.prof_sheet.update(f"U{prof_index}", disponible)
                logger.info(f"✅ Disponibilidad actualizada: {disponible}")
            
            return True, "Estado actualizado correctamente"
            
        except Exception as e:
            logger.error(f"❌ Error actualizando estado profesional: {e}")
            return False, "Error interno del servidor"

    def get_professional_by_id(self, user_id):
        """Obtener datos completos de un profesional por ID"""
        try:
            # Obtener hoja de profesionales
            try:
                prof_sheet = self.spreadsheet.worksheet("Profesionales")
                users_sheet = self.spreadsheet.worksheet("Usuarios")
            except gspread.exceptions.WorksheetNotFound:
                logger.error("❌ Hojas no encontradas")
                return None
            
            # Obtener datos con manejo robusto de headers
            def get_records_robust(sheet):
                try:
                    # Obtener todos los valores
                    all_values = sheet.get_all_values()
                    if not all_values:
                        return []
                    
                    # Obtener headers
                    headers = all_values[0]
                    
                    # Verificar headers duplicados y corregirlos
                    headers_unicos = []
                    headers_corregidos = []
                    contadores = {}
                    
                    for header in headers:
                        if header in contadores:
                            contadores[header] += 1
                            header_corregido = f"{header}_{contadores[header]}"
                        else:
                            contadores[header] = 0
                            header_corregido = header
                        
                        headers_corregidos.append(header_corregido)
                        headers_unicos.append(header_corregido)
                    
                    # Crear registros con headers corregidos
                    records = []
                    for row in all_values[1:]:
                        record = {}
                        for i, value in enumerate(row):
                            if i < len(headers_corregidos):
                                record[headers_corregidos[i]] = value
                        records.append(record)
                    
                    return records
                except Exception as e:
                    logger.error(f"❌ Error obteniendo registros: {e}")
                    return []
            
            # Obtener datos con manejo robusto
            prof_records = get_records_robust(prof_sheet)
            user_records = get_records_robust(users_sheet)
            
            professional_data = None
            user_data = None
            
            # Buscar datos profesionales
            for record in prof_records:
                if str(record.get("ID", "")) == str(user_id):
                    professional_data = record
                    logger.info(
                        f"✅ Datos profesionales encontrados: {professional_data}"
                    )
                    break
                
            # Buscar datos de usuario (para obtener el género)
            for record in user_records:
                if str(record.get("id", "")) == str(user_id):
                    user_data = record
                    logger.info(f"✅ Datos de usuario encontrados: {user_data}")
                    break
            
            if professional_data and user_data:
                # Combinar datos profesionales con el género del usuario
                professional_data["genero"] = user_data.get("genero", "")
                logger.info(f"✅ Datos combinados: {professional_data}")
                return professional_data
            
            logger.error("❌ No se encontraron datos completos")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo profesional: {e}")
            return None

    def add_professional_certification(
        self, user_id, titulo, institucion, ano, archivo_url=""
    ):
        """Agregar certificación a un profesional"""
        try:
            # Obtener o crear hoja de certificaciones
            try:
                cert_sheet = self.spreadsheet.worksheet("Certificaciones")
            except gspread.exceptions.WorksheetNotFound:
                # Crear hoja si no existe
                cert_sheet = self.spreadsheet.add_worksheet(
                    title="Certificaciones", rows=1000, cols=10
                )
                # Agregar encabezados
                headers = [
                    "ID",
                    "Profesional_ID",
                    "Titulo",
                    "Institucion",
                    "Ano",
                    "Archivo_URL",
                    "Fecha_Agregado",
                    "Estado",
                    "Verificado",
                ]
                cert_sheet.append_row(headers)
                logger.info("✅ Hoja 'Certificaciones' creada")
            
            # Generar ID único para la certificación
            try:
                all_records = cert_sheet.get_all_records()
                if all_records:
                    max_id = max(
                        [
                            int(record.get("ID", 0))
                            for record in all_records
                            if record.get("ID")
                        ]
                    )
                    cert_id = max_id + 1
                else:
                    cert_id = 1
            except:
                cert_id = 1
            
            # Preparar datos de la certificación
            current_time = datetime.now().isoformat()
            cert_data = [
                cert_id,
                user_id,
                titulo,
                institucion,
                ano,
                archivo_url,
                current_time,
                "activo",
                "pendiente",  # verificación pendiente
            ]
            
            # Agregar certificación
            cert_sheet.append_row(cert_data)
            
            logger.info(
                f"✅ Certificación agregada - ID: {cert_id}, Profesional: {user_id}"
            )
            return True, "Certificación agregada exitosamente"
            
        except Exception as e:
            logger.error(f"❌ Error agregando certificación: {e}")
            return False, "Error interno del servidor"

    def get_professional_certifications(self, user_id):
        """Obtener todas las certificaciones de un profesional"""
        try:
            # Obtener hoja de certificaciones
            try:
                cert_sheet = self.spreadsheet.worksheet("Certificaciones")
            except gspread.exceptions.WorksheetNotFound:
                return []
            
            # Buscar certificaciones del profesional
            all_records = cert_sheet.get_all_records()
            certifications = []
            
            for record in all_records:
                if str(record.get("Profesional_ID", "")) == str(user_id):
                    certifications.append(record)
            
            return certifications
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo certificaciones: {e}")
            return []

    def update_professional_profile(self, user_id, form_data):
        """Actualizar el perfil de un profesional"""
        try:
            # Obtener hoja de profesionales
            try:
                prof_sheet = self.spreadsheet.worksheet("Profesionales")
            except gspread.exceptions.WorksheetNotFound:
                return False, "Hoja de profesionales no encontrada"
            
            # Buscar el profesional por ID
            all_records = prof_sheet.get_all_records()
            professional_row = None
            row_index = None
            
            for i, record in enumerate(all_records):
                if str(record.get("ID", "")) == str(user_id):
                    professional_row = record
                    row_index = i + 2  # +2 porque enumerate empieza en 0 y hay header
                    break
            
            if not professional_row:
                return False, "Profesional no encontrado"
            
            # Mapear campos del formulario a columnas de la hoja
            field_mapping = {
                # Información profesional
                "numero_registro": "F",  # Columna F
                "especialidad": "G",  # Columna G
                "anos_experiencia": "H",  # Columna H
                "idiomas": "L",  # Columna L
                # Información de contacto
                "email": "B",  # Columna B
                "telefono": "E",  # Columna E
                "direccion_consulta": "J",  # Columna J
                "horario_atencion": "K",  # Columna K
            }
            
            # Actualizar campos modificados
            updates = []
            for field, column in field_mapping.items():
                if field in form_data:
                    value = str(form_data[field]).strip()
                    cell_address = f"{column}{row_index}"
                    updates.append({"range": cell_address, "values": [[value]]})
                    logger.info(f"📝 Actualizando {field}: {value} en {cell_address}")
            
            # Aplicar todas las actualizaciones
            if updates:
                # Usar actualizaciones individuales para evitar errores de formato
                for update in updates:
                    cell_address = update["range"]
                    value = update["values"][0][0]  # Extraer el valor
                    prof_sheet.update(cell_address, [[value]])
                    logger.info(f"✅ Campo actualizado: {cell_address} = {value}")
                
                logger.info(
                    f"✅ Perfil profesional actualizado - {len(updates)} campos"
                )
                return True, "Perfil actualizado correctamente"
            else:
                return True, "No hay cambios para actualizar"
                
        except Exception as e:
            logger.error(f"❌ Error actualizando perfil profesional: {e}")
            return False, "Error interno del servidor"

    def get_all_users(self):
        """Obtener todos los usuarios"""
        try:
            all_records = self.users_sheet.get_all_records()
            return all_records
        except Exception as e:
            logger.error(f"❌ Error obteniendo todos los usuarios: {e}")
            return []
    
    def get_user_count(self):
        """Obtener el número total de usuarios"""
        try:
            all_records = self.users_sheet.get_all_records()
            return len(all_records)
        except Exception as e:
            logger.error(f"❌ Error contando usuarios: {e}")
            return 0
    
    def get_professional_count(self):
        """Obtener el número total de profesionales"""
        try:
            prof_sheet = self.spreadsheet.worksheet("Profesionales")
            all_records = prof_sheet.get_all_records()
            return len(all_records)
        except Exception as e:
            logger.error(f"❌ Error contando profesionales: {e}")
            return 0
    
    def get_patient_count(self):
        """Obtener el número total de pacientes"""
        try:
            # Intentar obtener hoja de pacientes
            try:
                patient_sheet = self.spreadsheet.worksheet("Pacientes_Profesional")
                all_records = patient_sheet.get_all_records()
                return len(all_records)
            except gspread.exceptions.WorksheetNotFound:
                return 0
        except Exception as e:
            logger.error(f"❌ Error contando pacientes: {e}")
            return 0
    
    def get_atencion_count(self):
        """Obtener el número total de atenciones"""
        try:
            # Intentar obtener hoja de atenciones
            try:
                atencion_sheet = self.spreadsheet.worksheet("Atenciones_Medicas")
                all_records = atencion_sheet.get_all_records()
                return len(all_records)
            except gspread.exceptions.WorksheetNotFound:
                return 0
        except Exception as e:
            logger.error(f"❌ Error contando atenciones: {e}")
            return 0
    
    def get_sheet_info(self):
        """Obtener información de todas las hojas"""
        try:
            sheets_info = {}
            for worksheet in self.spreadsheet.worksheets():
                try:
                    records = worksheet.get_all_records()
                    sheets_info[worksheet.title] = {
                        "row_count": len(records),
                        "column_count": len(records[0]) if records else 0,
                        "status": "OK",
                    }
                except Exception as e:
                    sheets_info[worksheet.title] = {
                        "row_count": 0,
                        "column_count": 0,
                        "status": f"ERROR: {str(e)}",
                    }
            return sheets_info
        except Exception as e:
            logger.error(f"❌ Error obteniendo información de hojas: {e}")
            return {}
    
    def test_connection(self):
        """Probar la conexión con Google Sheets"""
        try:
            # Intentar acceder a una hoja
            test_sheet = self.spreadsheet.worksheet("Usuarios")
            test_records = test_sheet.get_all_records()
            return {
                "status": "OK",
                "message": "Conexión exitosa",
                "user_count": len(test_records),
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Error de conexión: {str(e)}",
                "user_count": 0,
            }

    def debug_user_complete(self, email):
        """Debugging completo de un usuario específico"""
        try:
            logger.info(f"🔍 === DEBUG COMPLETO PARA {email} ===")
            
            # Obtener headers de la hoja
            try:
                headers = self.users_sheet.row_values(1)
                logger.info(f"📋 Headers en Google Sheets: {headers}")
                
                if "password_hash" not in headers:
                    logger.error(
                        "❌ PROBLEMA CRÍTICO: La columna 'password_hash' no existe en los headers"
                    )
                    return None
                else:
                    password_index = headers.index("password_hash") + 1
                    logger.info(
                        f"✅ Columna 'password_hash' encontrada en posición {password_index}"
                    )
            except Exception as e:
                logger.error(f"❌ Error obteniendo headers: {e}")
                return None
            
            # Obtener todos los registros
            all_records = self.users_sheet.get_all_records()
            logger.info(f"📊 Total de usuarios en Sheets: {len(all_records)}")
            
            # Buscar el usuario específico
            user_record = None
            row_number = None
            for i, record in enumerate(all_records):
                if record.get("email", "").lower() == email.lower():
                    user_record = record
                    row_number = i + 2  # +2 porque enumerate empieza en 0 y hay header
                    logger.info(f"✅ Usuario encontrado en fila {row_number}")
                    break
            
            if not user_record:
                logger.error(f"❌ Usuario {email} no encontrado en Sheets")
                logger.info("📋 Usuarios existentes (primeros 5):")
                for i, record in enumerate(all_records[:5]):
                    logger.info(f"  {i+1}. {record.get('email', 'SIN EMAIL')}")
                return None
            
            # Mostrar todos los campos del usuario
            logger.info("📋 Datos del usuario desde get_all_records():")
            for key, value in user_record.items():
                if key == "password_hash":
                    if value:
                        logger.info(
                            f"  🔐 {key}: [HASH PRESENTE - {len(value)} caracteres]"
                        )
                        logger.info(f"  🔍 Primeros 30 chars del hash: {value[:30]}...")
                        logger.info(
                            f"  ✓ Hash válido: {self.is_valid_bcrypt_hash(value)}"
                        )
                    else:
                        logger.error(f"  ❌ {key}: [VACÍO - ESTE ES EL PROBLEMA]")
                else:
                    logger.info(f"  📝 {key}: {value}")
            
            # Verificar datos raw de la fila específica
            logger.info(f"📊 Datos raw de la fila {row_number}:")
            try:
                raw_values = self.users_sheet.row_values(row_number)
                for j, val in enumerate(raw_values):
                    header_name = headers[j] if j < len(headers) else f"Columna{j+1}"
                    if header_name == "password_hash":
                        if val:
                            logger.info(
                                f"  🔐 Columna {j+1} ({header_name}): [HASH RAW - {len(val)} chars] {val[:30]}..."
                            )
                        else:
                            logger.error(
                                f"  ❌ Columna {j+1} ({header_name}): [VACÍO EN RAW]"
                            )
                    else:
                        logger.info(f"  📝 Columna {j+1} ({header_name}): {val}")
            except Exception as e:
                logger.error(f"❌ Error obteniendo datos raw: {e}")
            
            return user_record
            
        except Exception as e:
            logger.error(f"❌ Error en debug completo: {e}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    def fix_user_password(self, email, new_password="TempPassword123!"):
        """Reparar la contraseña de un usuario específico"""
        try:
            logger.info(f"🛠️ === REPARANDO CONTRASEÑA PARA {email} ===")
            
            # Buscar usuario
            all_records = self.users_sheet.get_all_records()
            user_record = None
            row_number = None
            
            for i, record in enumerate(all_records):
                if record.get("email", "").lower() == email.lower():
                    user_record = record
                    row_number = i + 2  # +2 porque enumerate empieza en 0 y hay header
                    break
            
            if not user_record:
                logger.error(f"❌ Usuario {email} no encontrado para reparar")
                return False, "Usuario no encontrado"
            
            # Generar nuevo hash
            logger.info(f"🔐 Generando nuevo hash para contraseña: {new_password}")
            new_hash = self.hash_password(new_password)
            
            # Obtener índice de columna password
            headers = self.users_sheet.row_values(1)
            if "password_hash" not in headers:
                logger.error(
                    "❌ No se puede reparar: columna 'password_hash' no existe"
                )
                return False, "Columna password_hash no encontrada"
            
            password_col_index = headers.index("password_hash") + 1
            password_col_letter = chr(ord("A") + password_col_index - 1)
            
            logger.info(f"📍 Actualizando celda {password_col_letter}{row_number}")
            
            # Actualizar contraseña en Google Sheets
            self.users_sheet.update(f"{password_col_letter}{row_number}", new_hash)
            
            logger.info(f"✅ Contraseña reparada para {email}")
            logger.info(f"🔑 Nueva contraseña: {new_password}")
            
            # Verificar inmediatamente que se guardó
            logger.info("🔍 Verificando que la reparación fue exitosa...")
            verification = self.debug_user_complete(email)
            
            return True, f"Contraseña reparada. Nueva contraseña: {new_password}"
            
        except Exception as e:
            logger.error(f"❌ Error reparando contraseña: {e}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            return False, "Error interno reparando contraseña"

    def login_user_debug(self, email, password):
        """Login con debugging completo"""
        try:
            logger.info(f"🚀 === LOGIN CON DEBUG PARA {email} ===")
            
            # Primero hacer debug completo del usuario
            user_record = self.debug_user_complete(email)
            
            if not user_record:
                return False, "Email o contraseña incorrectos"
            
            # Verificar contraseña
            stored_hash = user_record.get("password_hash", "")
            
            if not stored_hash:
                logger.error(
                    f"❌ PROBLEMA IDENTIFICADO: Hash de contraseña vacío para {email}"
                )
                logger.error("💡 SOLUCIONES DISPONIBLES:")
                logger.error(
                    "   1. Usar auth_manager.fix_user_password(email) para reparar"
                )
                logger.error("   2. El usuario debe restablecer su contraseña")
                
                return (
                    False,
                    "Su contraseña no está configurada correctamente. Contacte al administrador o use la función de reparación.",
                )
            
            logger.info(f"🔍 Verificando contraseña para {email}...")
            logger.info(f"�� Hash almacenado: {len(stored_hash)} caracteres")
            
            # Verificar que el hash es válido
            if not self.is_valid_bcrypt_hash(stored_hash):
                logger.error(
                    f"❌ Hash bcrypt inválido para {email}: {stored_hash[:30]}..."
                )
                return (
                    False,
                    "Hash de contraseña corrupto. Use la función de reparación.",
                )
            
            # Verificar contraseña
            if not self.verify_password(password, stored_hash):
                logger.warning(f"❌ Contraseña incorrecta para {email}")
                return False, "Email o contraseña incorrectos"
            
            # Actualizar último acceso
            try:
                all_records = self.users_sheet.get_all_records()
                row_index = None
                for i, record in enumerate(all_records):
                    if record.get("email", "").lower() == email.lower():
                        row_index = i + 2
                        break
                
                if row_index:
                    self.users_sheet.update(f"L{row_index}", datetime.now().isoformat())
                    logger.info(
                        f"✅ Último acceso actualizado: {datetime.now().isoformat()}"
                    )
            except Exception as e:
                logger.warning(f"⚠️ No se pudo actualizar último acceso: {e}")
            
            logger.info(f"✅ Login exitoso para {email}")
            return True, "Login exitoso"
            
        except Exception as e:
            logger.error(f"❌ Error en login con debug: {e}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            return False, "Error interno del servidor"

    def is_connected(self):
        """Verificar si está conectado a Google Sheets"""
        return (
            not self.use_fallback
            and self.gc is not None
            and self.spreadsheet is not None
        )


# Crear instancia global (se inicializa cuando se importa el módulo)
try:
    auth_manager = AuthManager()
    logger.info("✅ AuthManager inicializado correctamente")
except Exception as e:
    logger.error(f"❌ Error inicializando AuthManager: {e}")
    auth_manager = None
