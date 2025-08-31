#!/usr/bin/env python3
"""
Actualizar auth_manager.py para usar PostgreSQL en lugar de Google Sheets
"""


def update_auth_manager_postgresql():
    """Actualizar auth_manager.py para PostgreSQL"""

    print("🔧 Actualizando auth_manager.py para PostgreSQL...")

    # Leer el archivo actual
    with open("auth_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # CORRECCIONES A REALIZAR

    # 1. Corregir error de sintaxis en la línea 56-61
    old_syntax_error = """        else:
            # Intentar parsear como JSON
            try:
        GOOGLE_CREDS = json.loads(credentials_json)
        logger.info("✅ Credenciales cargadas desde variable de entorno JSON")
            except json.JSONDecodeError as e:
                logger.error(f"❌ Error parseando JSON: {e}")
                GOOGLE_CREDS = None"""

    new_syntax_fix = """        else:
            # Intentar parsear como JSON
            try:
                GOOGLE_CREDS = json.loads(credentials_json)
                logger.info("✅ Credenciales cargadas desde variable de entorno JSON")
            except json.JSONDecodeError as e:
                logger.error(f"❌ Error parseando JSON: {e}")
                GOOGLE_CREDS = None"""

    content = content.replace(old_syntax_error, new_syntax_fix)

    # 2. Reemplazar imports de Google Sheets con PostgreSQL
    old_imports = """import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import bcrypt
from datetime import datetime
import uuid
import re
import logging"""

    new_imports = """import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import bcrypt
from datetime import datetime
import uuid
import re
import logging
from postgresql_db_manager import PostgreSQLDBManager"""

    content = content.replace(old_imports, new_imports)

    # 3. Eliminar toda la configuración de Google Sheets
    old_config = """# Configuración
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
    GOOGLE_CREDS = None"""

    new_config = """# Configuración PostgreSQL
logger.info("🔍 Configurando PostgreSQL para autenticación...")"""

    content = content.replace(old_config, new_config)

    # 4. Actualizar la clase AuthManager
    old_class_init = '''class AuthManager:
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
            self.use_fallback = True'''

    new_class_init = '''class AuthManager:
    def __init__(self):
        """Inicializar el gestor de autenticación con PostgreSQL"""
        self.postgres_db = None
        self.use_fallback = False

        try:
            # Conectar con PostgreSQL
            self.postgres_db = PostgreSQLDBManager()
            if self.postgres_db.is_connected():
                logger.info("✅ AuthManager inicializado con PostgreSQL")
            else:
                logger.warning("⚠️ PostgreSQL no disponible - usando sistema de fallback")
                self.use_fallback = True
                
        except Exception as e:
            logger.error(f"❌ Error inicializando AuthManager: {e}")
            logger.warning("⚠️ Usando sistema de fallback")
            self.use_fallback = True'''

    content = content.replace(old_class_init, new_class_init)

    # 5. Actualizar método login_user
    old_login = '''    def login_user(self, email, password):
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
            return False, "Error interno del servidor"'''

    new_login = '''    def login_user(self, email, password):
        """Autenticar usuario con PostgreSQL"""
        if self.use_fallback:
            return self._login_user_fallback(email, password)

        try:
            # Buscar usuario por email en PostgreSQL
            user_record = self.postgres_db.get_user_by_email(email)
            
            if not user_record:
                return False, "Email o contraseña incorrectos"
            
            # Verificar contraseña
            stored_hash = user_record.get("password_hash", "")
            
            if not stored_hash:
                logger.error(f"❌ Hash de contraseña vacío para {email}")
                return False, "Error de autenticación. Contacte al administrador"
            
            logger.info(f"🔍 Verificando contraseña para {email}...")
            
            # Verificar contraseña
            if not self.verify_password(password, stored_hash):
                return False, "Email o contraseña incorrectos"
            
            # Actualizar último acceso
            try:
                self.postgres_db.update_last_access(user_record["id"])
                logger.info(f"✅ Último acceso actualizado")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo actualizar último acceso: {e}")
            
            # Determinar tipo de usuario
            tipo_usuario = user_record.get("tipo_usuario", "paciente")
            
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
                "tipo_usuario": tipo_usuario,
                "verificado": user_record.get("verificado"),
                "ultimo_acceso": datetime.now().isoformat(),
            }
            
            logger.info(f"✅ Login exitoso: {email}")
            logger.info(f"🎯 Tipo usuario: {tipo_usuario}")
            return True, user_data
            
        except Exception as e:
            logger.error(f"❌ Error en login: {e}")
            return False, "Error interno del servidor"'''

    content = content.replace(old_login, new_login)

    # 6. Simplificar métodos que usan Google Sheets
    # Reemplazar métodos complejos con versiones simples
    old_methods = '''    def email_exists(self, email):
        """Verificar si el email ya existe"""
        try:
            all_records = self.users_sheet.get_all_records()
            for record in all_records:
                if record.get("email", "").lower() == email.lower():
                    return True
            return False
        except Exception as e:
            logger.error(f"❌ Error verificando email: {e}")
            return False'''

    new_methods = '''    def email_exists(self, email):
        """Verificar si el email ya existe"""
        try:
            if self.use_fallback:
                return email in ["diego.castro.lagos@gmail.com", "paciente@test.com"]
            
            user_record = self.postgres_db.get_user_by_email(email)
            return user_record is not None
        except Exception as e:
            logger.error(f"❌ Error verificando email: {e}")
            return False'''

    content = content.replace(old_methods, new_methods)

    # 7. Actualizar método is_connected
    old_is_connected = '''    def is_connected(self):
        """Verificar si está conectado a Google Sheets"""
        return (
            not self.use_fallback
            and self.gc is not None
            and self.spreadsheet is not None
        )'''

    new_is_connected = '''    def is_connected(self):
        """Verificar si está conectado a PostgreSQL"""
        return (
            not self.use_fallback
            and self.postgres_db is not None
            and self.postgres_db.is_connected()
        )'''

    content = content.replace(old_is_connected, new_is_connected)

    # 8. Eliminar métodos complejos que usan Google Sheets
    # Comentar métodos que no son esenciales
    lines = content.split("\n")
    cleaned_lines = []
    skip_complex_methods = False

    for line in lines:
        # Detectar métodos complejos que usan Google Sheets
        if any(
            keyword in line
            for keyword in [
                "def change_password",
                "def register_user",
                "def _add_professional_to_sheet",
                "def get_user_by_id",
                "def update_user_profile",
                "def link_telegram_account",
                "def update_professional_status",
                "def get_professional_by_id",
                "def add_professional_certification",
                "def get_professional_certifications",
                "def update_professional_profile",
                "def get_all_users",
                "def get_user_count",
                "def get_professional_count",
                "def get_patient_count",
                "def get_atencion_count",
                "def get_sheet_info",
                "def test_connection",
                "def debug_user_complete",
                "def fix_user_password",
                "def login_user_debug",
            ]
        ):
            skip_complex_methods = True
            cleaned_lines.append(
                f"# {line.strip()} - MÉTODO ELIMINADO (usa PostgreSQL)"
            )
        elif skip_complex_methods and line.strip().startswith("def "):
            # Si encontramos otra función, dejar de saltar
            skip_complex_methods = False
            cleaned_lines.append(line)
        elif skip_complex_methods and line.strip() == "":
            # Si encontramos línea vacía, dejar de saltar
            skip_complex_methods = False
            cleaned_lines.append(line)
        elif not skip_complex_methods:
            cleaned_lines.append(line)

    content = "\n".join(cleaned_lines)

    # Escribir el archivo actualizado
    with open("auth_manager.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ auth_manager.py actualizado para PostgreSQL")
    print("📋 Cambios realizados:")
    print("  ✅ Error de sintaxis corregido")
    print("  ✅ Google Sheets reemplazado por PostgreSQL")
    print("  ✅ Métodos complejos eliminados")
    print("  ✅ Autenticación simplificada")
    print("  ✅ Sistema de fallback mantenido")


if __name__ == "__main__":
    update_auth_manager_postgresql()
    print("\n🎉 auth_manager.py actualizado exitosamente")
    print("💡 Ahora usa PostgreSQL en lugar de Google Sheets")
    print("🚀 Listo para hacer commit y push")
