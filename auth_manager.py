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
        'GOOGLE_SERVICE_ACCOUNT_JSON': bool(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')),
        'GOOGLE_CREDENTIALS_FILE': bool(os.environ.get('GOOGLE_CREDENTIALS_FILE')),
        'GOOGLE_SHEETS_ID': bool(os.environ.get('GOOGLE_SHEETS_ID'))
    }
    logger.info(f"🔧 Variables de entorno disponibles: {env_vars}")
    
    # Intentar cargar desde JSON en variable de entorno
    if os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'):
        logger.info("📄 Cargando credenciales desde GOOGLE_SERVICE_ACCOUNT_JSON...")
        credentials_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        GOOGLE_CREDS = json.loads(credentials_json)
        logger.info("✅ Credenciales cargadas desde variable de entorno JSON")
    # Intentar cargar desde archivo
    elif os.environ.get('GOOGLE_CREDENTIALS_FILE'):
        logger.info("📁 Cargando credenciales desde archivo...")
        credentials_file = os.environ.get('GOOGLE_CREDENTIALS_FILE')
        with open(credentials_file, 'r') as f:
            GOOGLE_CREDS = json.load(f)
        logger.info("✅ Credenciales cargadas desde archivo")
    # Intentar archivos por defecto
    else:
        logger.info("🔍 Buscando archivos de credenciales por defecto...")
        possible_files = [
            'credentials.json',
            'service-account.json',
            'google-credentials.json',
            'medconnect-credentials.json'
        ]
        GOOGLE_CREDS = None
        for file_path in possible_files:
            if os.path.exists(file_path):
                logger.info(f"📁 Encontrado archivo: {file_path}")
                with open(file_path, 'r') as f:
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
        try:
            if GOOGLE_CREDS is None:
                raise Exception("Credenciales de Google no disponibles")
                
            # Conectar con Google Sheets
            credentials = Credentials.from_service_account_info(
                GOOGLE_CREDS, 
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.gc = gspread.authorize(credentials)
            self.spreadsheet = self.gc.open_by_key(GOOGLE_SHEETS_ID)
            
            # Obtener hoja de usuarios
            try:
                self.users_sheet = self.spreadsheet.worksheet('Usuarios')
            except gspread.exceptions.WorksheetNotFound:
                logger.error("❌ Hoja 'Usuarios' no encontrada. Ejecuta setup_auth_sheets.py primero.")
                raise Exception("Hoja de usuarios no configurada")
                
            logger.info("✅ AuthManager inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando AuthManager: {e}")
            raise

    def validate_email(self, email):
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_password(self, password):
        """Validar fortaleza de contraseña"""
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        if not re.search(r'[A-Za-z]', password):
            return False, "La contraseña debe contener al menos una letra"
        if not re.search(r'[0-9]', password):
            return False, "La contraseña debe contener al menos un número"
        return True, "Contraseña válida"

    def hash_password(self, password):
        """Hashear contraseña usando bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password, hashed):
        """Verificar contraseña hasheada"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def email_exists(self, email):
        """Verificar si el email ya existe"""
        try:
            all_records = self.users_sheet.get_all_records()
            for record in all_records:
                if record.get('email', '').lower() == email.lower():
                    return True
            return False
        except Exception as e:
            logger.error(f"Error verificando email: {e}")
            return False

    def get_next_user_id(self):
        """Obtener el siguiente ID de usuario disponible"""
        try:
            all_records = self.users_sheet.get_all_records()
            if not all_records:
                return 1
            
            max_id = max([int(record.get('id', 0)) for record in all_records if record.get('id')])
            return max_id + 1
        except Exception as e:
            logger.error(f"Error obteniendo siguiente ID: {e}")
            return 1

    def register_user(self, user_data):
        """
        Registrar nuevo usuario
        user_data debe contener: email, password, nombre, apellido, telefono, 
        fecha_nacimiento, genero, direccion, ciudad, tipo_usuario
        Para profesionales también incluye: profesion, especialidad, numero_registro, etc.
        """
        try:
            # Validaciones
            if not self.validate_email(user_data['email']):
                return False, "Formato de email inválido"
            
            if self.email_exists(user_data['email']):
                return False, "El email ya está registrado"
            
            is_valid, msg = self.validate_password(user_data['password'])
            if not is_valid:
                return False, msg
            
            # Campos requeridos
            required_fields = ['email', 'password', 'nombre', 'apellido', 'tipo_usuario']
            for field in required_fields:
                if not user_data.get(field):
                    return False, f"El campo {field} es requerido"
            
            # Validaciones específicas para profesionales
            if user_data['tipo_usuario'] == 'profesional':
                professional_required = ['profesion', 'numero_registro', 'institucion', 'titulo']
                for field in professional_required:
                    if not user_data.get(field):
                        return False, f"Para profesionales, el campo {field} es requerido"
            
            # Preparar datos del usuario
            user_id = self.get_next_user_id()
            password_hash = self.hash_password(user_data['password'])
            current_time = datetime.now().isoformat()
            
            row_data = [
                user_id,
                user_data['email'].lower(),
                password_hash,
                user_data['nombre'],
                user_data['apellido'],
                user_data.get('telefono', ''),
                user_data.get('fecha_nacimiento', ''),
                user_data.get('genero', ''),
                user_data.get('direccion', ''),
                user_data.get('ciudad', ''),
                current_time,  # fecha_registro
                '',  # ultimo_acceso
                'activo',  # estado
                user_data['tipo_usuario'],  # tipo_usuario (paciente/profesional)
                'false'  # verificado
            ]
            
            # Agregar usuario a la hoja
            self.users_sheet.append_row(row_data)
            
            # Si es profesional, agregar a la hoja de profesionales
            if user_data['tipo_usuario'] == 'profesional':
                self._add_professional_to_sheet(user_id, user_data)
            
            logger.info(f"✅ Usuario registrado: {user_data['email']}")
            return True, "Usuario registrado exitosamente"
            
        except Exception as e:
            logger.error(f"❌ Error registrando usuario: {e}")
            return False, "Error interno del servidor"

    def _add_professional_to_sheet(self, user_id, user_data):
        """Agregar profesional a la hoja de profesionales"""
        try:
            # Obtener o crear hoja de profesionales
            try:
                prof_sheet = self.spreadsheet.worksheet('Profesionales')
            except gspread.exceptions.WorksheetNotFound:
                # Crear hoja si no existe
                prof_sheet = self.spreadsheet.add_worksheet(title='Profesionales', rows=1000, cols=25)
                # Agregar encabezados
                headers = [
                    'ID', 'Email', 'Nombre', 'Apellido', 'Telefono', 'Numero_Registro',
                    'Especialidad', 'Anos_Experiencia', 'Profesion', 'Direccion_Consulta',
                    'Horario_Atencion', 'Idiomas', 'Certificaciones', 'Titulo', 'Institucion',
                    'Fecha_Graduacion', 'Biografia', 'Foto_URL', 'Calificacion', 'Estado',
                    'Disponible', 'Fecha_Registro', 'Ultima_Actualizacion', 'Areas_Especializacion'
                ]
                prof_sheet.append_row(headers)
                logger.info("✅ Hoja 'Profesionales' creada")
            
            # Preparar datos del profesional
            prof_data = [
                user_id,
                user_data['email'].lower(),
                user_data['nombre'],
                user_data['apellido'],
                user_data.get('telefono', ''),
                user_data.get('numero_registro', ''),
                user_data.get('especialidad', ''),
                user_data.get('anos_experiencia', '0'),
                user_data.get('profesion', ''),
                user_data.get('direccion_consulta', ''),
                user_data.get('horario_atencion', ''),
                user_data.get('idiomas', 'Español'),
                user_data.get('certificaciones', ''),
                user_data.get('titulo', ''),
                user_data.get('institucion', ''),
                user_data.get('fecha_graduacion', ''),
                user_data.get('biografia', ''),
                user_data.get('foto_url', ''),
                '0.0',  # calificacion inicial
                'activo',  # estado
                'true',  # disponible
                datetime.now().isoformat(),  # fecha_registro
                datetime.now().isoformat(),  # ultima_actualizacion
                user_data.get('areas_especializacion', '')
            ]
            
            # Agregar profesional a la hoja
            prof_sheet.append_row(prof_data)
            logger.info(f"✅ Profesional agregado: {user_data['email']}")
            
        except Exception as e:
            logger.error(f"❌ Error agregando profesional: {e}")
            # No fallar el registro principal si esto falla

    def login_user(self, email, password):
        """
        Iniciar sesión de usuario
        Retorna (success, message, user_data)
        """
        try:
            if not email or not password:
                return False, "Email y contraseña son requeridos", None
            
            # Buscar usuario
            all_records = self.users_sheet.get_all_records()
            user_record = None
            row_index = None
            
            for i, record in enumerate(all_records, start=2):  # Start=2 porque row 1 son headers
                if record.get('email', '').lower() == email.lower():
                    user_record = record
                    row_index = i
                    break
            
            if not user_record:
                return False, "Email o contraseña incorrectos", None
            
            # Verificar contraseña
            if not self.verify_password(password, user_record['password_hash']):
                return False, "Email o contraseña incorrectos", None
            
            # Verificar estado del usuario
            if user_record.get('estado', '').lower() != 'activo':
                return False, "Cuenta desactivada. Contacte al administrador", None
            
            # Actualizar último acceso
            current_time = datetime.now().isoformat()
            try:
                self.users_sheet.update(f'L{row_index}', [[current_time]])  # Formato correcto para update
                logger.info(f"✅ Último acceso actualizado: {current_time}")
            except Exception as update_error:
                logger.warning(f"⚠️ Error actualizando último acceso: {update_error}")
                # Continuar con el login aunque falle la actualización
            
            # Preparar datos del usuario (sin password_hash)
            user_data = {
                'id': user_record['id'],
                'email': user_record['email'],
                'nombre': user_record['nombre'],
                'apellido': user_record['apellido'],
                'telefono': user_record.get('telefono', ''),
                'fecha_nacimiento': user_record.get('fecha_nacimiento', ''),
                'genero': user_record.get('genero', ''),
                'direccion': user_record.get('direccion', ''),
                'ciudad': user_record.get('ciudad', ''),
                'fecha_registro': user_record.get('fecha_registro', ''),
                'tipo_usuario': user_record['tipo_usuario'],
                'verificado': user_record.get('verificado', 'false'),
                'ultimo_acceso': current_time
            }
            
            logger.info(f"✅ Login exitoso: {email}")
            logger.info(f"🔍 Datos del usuario obtenidos: {user_data}")
            return True, "Login exitoso", user_data
            
        except Exception as e:
            logger.error(f"❌ Error en login: {e}")
            return False, "Error interno del servidor", None

    def get_user_by_id(self, user_id):
        """Obtener usuario por ID"""
        try:
            all_records = self.users_sheet.get_all_records()
            for record in all_records:
                if str(record.get('id', '')) == str(user_id):
                    # Remover password_hash de la respuesta
                    user_data = record.copy()
                    user_data.pop('password_hash', None)
                    return user_data
            return None
        except Exception as e:
            logger.error(f"Error obteniendo usuario: {e}")
            return None

    def update_user_profile(self, user_id, update_data):
        """Actualizar perfil de usuario"""
        try:
            all_records = self.users_sheet.get_all_records()
            row_index = None
            
            for i, record in enumerate(all_records, start=2):
                if str(record.get('id', '')) == str(user_id):
                    row_index = i
                    break
            
            if not row_index:
                return False, "Usuario no encontrado"
            
            # Campos actualizables
            updatable_fields = {
                'nombre': 'D', 'apellido': 'E', 'telefono': 'F', 
                'fecha_nacimiento': 'G', 'genero': 'H', 'direccion': 'I', 
                'ciudad': 'J'
            }
            
            # Actualizar campos
            for field, column in updatable_fields.items():
                if field in update_data:
                    self.users_sheet.update(f'{column}{row_index}', [[str(update_data[field])]])
            
            logger.info(f"✅ Perfil actualizado para usuario ID: {user_id}")
            return True, "Perfil actualizado exitosamente"
            
        except Exception as e:
            logger.error(f"❌ Error actualizando perfil: {e}")
            return False, "Error interno del servidor"

    def change_password(self, user_id, current_password, new_password):
        """Cambiar contraseña de usuario"""
        try:
            # Obtener usuario actual
            all_records = self.users_sheet.get_all_records()
            user_record = None
            row_index = None
            
            for i, record in enumerate(all_records, start=2):
                if str(record.get('id', '')) == str(user_id):
                    user_record = record
                    row_index = i
                    break
            
            if not user_record:
                return False, "Usuario no encontrado"
            
            # Verificar contraseña actual
            if not self.verify_password(current_password, user_record['password_hash']):
                return False, "Contraseña actual incorrecta"
            
            # Validar nueva contraseña
            is_valid, msg = self.validate_password(new_password)
            if not is_valid:
                return False, msg
            
            # Actualizar contraseña
            new_hash = self.hash_password(new_password)
            self.users_sheet.update(f'C{row_index}', [[new_hash]])  # Columna C = password_hash
            
            logger.info(f"✅ Contraseña cambiada para usuario ID: {user_id}")
            return True, "Contraseña actualizada exitosamente"
            
        except Exception as e:
            logger.error(f"❌ Error cambiando contraseña: {e}")
            return False, "Error interno del servidor"

    def get_user_by_email(self, email):
        """Obtener usuario por email"""
        try:
            all_records = self.users_sheet.get_all_records()
            for record in all_records:
                if record.get('email', '').lower() == email.lower():
                    # Remover password_hash de la respuesta
                    user_data = record.copy()
                    user_data.pop('password_hash', None)
                    return user_data
            return None
        except Exception as e:
            logger.error(f"Error obteniendo usuario por email: {e}")
            return None

    def get_user_by_telegram_id(self, telegram_id):
        """Obtener usuario por ID de Telegram"""
        try:
            all_records = self.users_sheet.get_all_records()
            for record in all_records:
                if str(record.get('telegram_id', '')) == str(telegram_id):
                    # Remover password_hash de la respuesta
                    user_data = record.copy()
                    user_data.pop('password_hash', None)
                    return user_data
            return None
        except Exception as e:
            logger.error(f"Error obteniendo usuario por Telegram ID: {e}")
            return None

    def link_telegram_account(self, email, telegram_id, telegram_username=""):
        """Vincular cuenta de Telegram con usuario existente"""
        try:
            all_records = self.users_sheet.get_all_records()
            row_index = None
            user_record = None
            
            # Buscar usuario por email
            for i, record in enumerate(all_records, start=2):
                if record.get('email', '').lower() == email.lower():
                    user_record = record
                    row_index = i
                    break
            
            if not user_record:
                return False, "Usuario no encontrado con ese email", None
            
            # Verificar si ya tiene Telegram vinculado
            if user_record.get('telegram_id'):
                return False, "Esta cuenta ya tiene un Telegram vinculado", None
            
            # Verificar si el Telegram ID ya está en uso
            for record in all_records:
                if str(record.get('telegram_id', '')) == str(telegram_id) and record.get('telegram_id'):
                    return False, "Este Telegram ya está vinculado a otra cuenta", None
            
            # Actualizar las columnas de Telegram
            # Asumo que las columnas están en las posiciones siguientes después de verificado:
            # P = telegram_id, Q = telegram_username
            try:
                self.users_sheet.update(f'P{row_index}', [[str(telegram_id)]])  # Columna P = telegram_id
                if telegram_username:
                    self.users_sheet.update(f'Q{row_index}', [[telegram_username]])  # Columna Q = telegram_username
                
                # Actualizar el registro en memoria
                user_record['telegram_id'] = str(telegram_id)
                user_record['telegram_username'] = telegram_username
                
            except Exception as sheet_error:
                logger.warning(f"Error actualizando columnas Telegram, intentando crear: {sheet_error}")
                # Si las columnas no existen, las creamos al final
                self._ensure_telegram_columns()
                # Reintentar
                self.users_sheet.update(f'P{row_index}', [[str(telegram_id)]])
                if telegram_username:
                    self.users_sheet.update(f'Q{row_index}', [[telegram_username]])
            
            logger.info(f"✅ Telegram vinculado para usuario: {email}")
            return True, f"Cuenta vinculada exitosamente para {user_record['nombre']} {user_record['apellido']}", user_record
            
        except Exception as e:
            logger.error(f"❌ Error vinculando Telegram: {e}")
            return False, "Error interno del servidor", None
    
    def _ensure_telegram_columns(self):
        """Asegura que las columnas de Telegram existan en la hoja"""
        try:
            # Obtener la primera fila (headers)
            headers = self.users_sheet.row_values(1)
            
            # Verificar si ya existen las columnas
            telegram_columns = ['telegram_id', 'telegram_username']
            missing_columns = []
            
            for col in telegram_columns:
                if col not in headers:
                    missing_columns.append(col)
            
            if missing_columns:
                # Agregar columnas faltantes
                start_col = len(headers) + 1
                for i, col_name in enumerate(missing_columns):
                    col_letter = self._number_to_letter(start_col + i)
                    self.users_sheet.update(f'{col_letter}1', [[col_name]])
                
                logger.info(f"✅ Columnas Telegram agregadas: {missing_columns}")
                
        except Exception as e:
            logger.error(f"Error asegurando columnas Telegram: {e}")
    
    def _number_to_letter(self, n):
        """Convierte un número de columna a letra (1=A, 2=B, etc.)"""
        result = ""
        while n > 0:
            n -= 1
            result = chr(n % 26 + ord('A')) + result
            n //= 26
        return result

    def link_telegram_by_user_id(self, user_id, telegram_id, telegram_username=""):
        """Vincular cuenta de Telegram con usuario por ID"""
        try:
            all_records = self.users_sheet.get_all_records()
            row_index = None
            user_record = None
            
            # Buscar usuario por ID
            for i, record in enumerate(all_records, start=2):
                if str(record.get('id', '')) == str(user_id):
                    user_record = record
                    row_index = i
                    break
            
            if not user_record:
                return False, "Usuario no encontrado", None
            
            # Verificar si ya tiene Telegram vinculado
            if user_record.get('telegram_id'):
                return False, "Esta cuenta ya tiene un Telegram vinculado", None
            
            # Verificar si el Telegram ID ya está en uso
            for record in all_records:
                if str(record.get('telegram_id', '')) == str(telegram_id) and record.get('telegram_id'):
                    return False, "Este Telegram ya está vinculado a otra cuenta", None
            
            # Actualizar las columnas de Telegram
            try:
                self.users_sheet.update(f'P{row_index}', [[str(telegram_id)]])  # Columna P = telegram_id
                if telegram_username:
                    self.users_sheet.update(f'Q{row_index}', [[telegram_username]])  # Columna Q = telegram_username
                
                # Actualizar el registro en memoria
                user_record['telegram_id'] = str(telegram_id)
                user_record['telegram_username'] = telegram_username
                
            except Exception as sheet_error:
                logger.warning(f"Error actualizando columnas Telegram, intentando crear: {sheet_error}")
                # Si las columnas no existen, las creamos al final
                self._ensure_telegram_columns()
                # Reintentar
                self.users_sheet.update(f'P{row_index}', [[str(telegram_id)]])
                if telegram_username:
                    self.users_sheet.update(f'Q{row_index}', [[telegram_username]])
            
            logger.info(f"✅ Telegram vinculado para usuario ID: {user_id}")
            return True, f"Cuenta vinculada exitosamente", user_record
            
        except Exception as e:
            logger.error(f"❌ Error vinculando Telegram por ID: {e}")
            return False, "Error interno del servidor", None
    
    def update_professional_status(self, user_id, estado=None, disponible=None):
        """
        Actualizar estado y disponibilidad de un profesional
        estado: 'activo', 'inactivo', 'suspendido'
        disponible: 'true', 'false'
        """
        try:
            # Obtener hoja de profesionales
            try:
                prof_sheet = self.spreadsheet.worksheet('Profesionales')
            except gspread.exceptions.WorksheetNotFound:
                return False, "Hoja de profesionales no encontrada"
            
            # Buscar profesional por ID
            all_records = prof_sheet.get_all_records()
            row_index = None
            
            for i, record in enumerate(all_records, start=2):  # Start=2 porque row 1 son headers
                if str(record.get('ID', '')) == str(user_id):
                    row_index = i
                    break
            
            if not row_index:
                return False, "Profesional no encontrado"
            
            # Actualizar estado (columna T - posición 20)
            if estado is not None:
                if estado not in ['activo', 'inactivo', 'suspendido']:
                    return False, "Estado debe ser: activo, inactivo o suspendido"
                prof_sheet.update(f'T{row_index}', [[estado]])
                logger.info(f"✅ Estado actualizado a '{estado}' para profesional ID: {user_id}")
            
            # Actualizar disponibilidad (columna U - posición 21)
            if disponible is not None:
                if disponible not in ['true', 'false']:
                    return False, "Disponible debe ser: true o false"
                prof_sheet.update(f'U{row_index}', [[disponible]])
                logger.info(f"✅ Disponibilidad actualizada a '{disponible}' para profesional ID: {user_id}")
            
            return True, "Estado del profesional actualizado exitosamente"
            
        except Exception as e:
            logger.error(f"❌ Error actualizando estado del profesional: {e}")
            return False, "Error interno del servidor"

    def get_professional_by_id(self, user_id):
        """Obtener datos completos de un profesional por ID"""
        try:
            # Obtener hoja de profesionales
            try:
                prof_sheet = self.spreadsheet.worksheet('Profesionales')
                users_sheet = self.spreadsheet.worksheet('Usuarios')
            except gspread.exceptions.WorksheetNotFound:
                logger.error("❌ Hojas no encontradas")
                return None
            
            # Buscar profesional y datos de usuario
            prof_records = prof_sheet.get_all_records()
            user_records = users_sheet.get_all_records()
            
            professional_data = None
            user_data = None
            
            # Buscar datos profesionales
            for record in prof_records:
                if str(record.get('ID', '')) == str(user_id):
                    professional_data = record
                    logger.info(f"✅ Datos profesionales encontrados: {professional_data}")
                    break
                
            # Buscar datos de usuario (para obtener el género)
            for record in user_records:
                if str(record.get('id', '')) == str(user_id):
                    user_data = record
                    logger.info(f"✅ Datos de usuario encontrados: {user_data}")
                    break
            
            if professional_data and user_data:
                # Combinar datos profesionales con el género del usuario
                professional_data['genero'] = user_data.get('genero', '')
                logger.info(f"✅ Datos combinados: {professional_data}")
                return professional_data
            
            logger.error("❌ No se encontraron datos completos")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo profesional: {e}")
            return None

    def add_professional_certification(self, user_id, titulo, institucion, ano, archivo_url=''):
        """Agregar certificación a un profesional"""
        try:
            # Obtener o crear hoja de certificaciones
            try:
                cert_sheet = self.spreadsheet.worksheet('Certificaciones')
            except gspread.exceptions.WorksheetNotFound:
                # Crear hoja si no existe
                cert_sheet = self.spreadsheet.add_worksheet(
                    title='Certificaciones', 
                    rows=1000, 
                    cols=10
                )
                # Agregar encabezados
                headers = [
                    'ID', 'Profesional_ID', 'Titulo', 'Institucion', 'Ano',
                    'Archivo_URL', 'Fecha_Agregado', 'Estado', 'Verificado'
                ]
                cert_sheet.append_row(headers)
                logger.info("✅ Hoja 'Certificaciones' creada")
            
            # Generar ID único para la certificación
            try:
                all_records = cert_sheet.get_all_records()
                if all_records:
                    max_id = max([int(record.get('ID', 0)) for record in all_records if record.get('ID')])
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
                'activo',
                'pendiente'  # verificación pendiente
            ]
            
            # Agregar certificación
            cert_sheet.append_row(cert_data)
            
            logger.info(f"✅ Certificación agregada - ID: {cert_id}, Profesional: {user_id}")
            return True, "Certificación agregada exitosamente"
            
        except Exception as e:
            logger.error(f"❌ Error agregando certificación: {e}")
            return False, "Error interno del servidor"

    def get_professional_certifications(self, user_id):
        """Obtener todas las certificaciones de un profesional"""
        try:
            # Obtener hoja de certificaciones
            try:
                cert_sheet = self.spreadsheet.worksheet('Certificaciones')
            except gspread.exceptions.WorksheetNotFound:
                return []
            
            # Buscar certificaciones del profesional
            all_records = cert_sheet.get_all_records()
            certifications = []
            
            for record in all_records:
                if str(record.get('Profesional_ID', '')) == str(user_id):
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
                prof_sheet = self.spreadsheet.worksheet('Profesionales')
            except gspread.exceptions.WorksheetNotFound:
                return False, "Hoja de profesionales no encontrada"
            
            # Buscar el profesional por ID
            all_records = prof_sheet.get_all_records()
            professional_row = None
            row_index = None
            
            for i, record in enumerate(all_records):
                if str(record.get('ID', '')) == str(user_id):
                    professional_row = record
                    row_index = i + 2  # +2 porque enumerate empieza en 0 y hay header
                    break
            
            if not professional_row:
                return False, "Profesional no encontrado"
            
            # Mapear campos del formulario a columnas de la hoja
            field_mapping = {
                # Información profesional
                'numero_registro': 'F',      # Columna F
                'especialidad': 'G',         # Columna G  
                'anos_experiencia': 'H',     # Columna H
                'idiomas': 'L',              # Columna L
                # Información de contacto
                'email': 'B',                # Columna B
                'telefono': 'E',             # Columna E
                'direccion_consulta': 'J',   # Columna J
                'horario_atencion': 'K'      # Columna K
            }
            
            # Actualizar campos modificados
            updates = []
            for field, column in field_mapping.items():
                if field in form_data:
                    value = str(form_data[field]).strip()
                    cell_address = f"{column}{row_index}"
                    updates.append({
                        'range': cell_address,
                        'values': [[value]]
                    })
                    logger.info(f"📝 Actualizando {field}: {value} en {cell_address}")
            
            # Aplicar todas las actualizaciones
            if updates:
                # Usar actualizaciones individuales para evitar errores de formato
                for update in updates:
                    cell_address = update['range']
                    value = update['values'][0][0]  # Extraer el valor
                    prof_sheet.update(cell_address, [[value]])
                    logger.info(f"✅ Campo actualizado: {cell_address} = {value}")
                
                logger.info(f"✅ Perfil profesional actualizado - {len(updates)} campos")
                return True, "Perfil actualizado correctamente"
            else:
                return True, "No hay cambios para actualizar"
                
        except Exception as e:
            logger.error(f"❌ Error actualizando perfil profesional: {e}")
            return False, "Error interno del servidor"
    

# Crear instancia global (se inicializa cuando se importa el módulo)
try:
    auth_manager = AuthManager()
    logger.info("✅ AuthManager global inicializado")
except Exception as e:
    logger.error(f"❌ Error inicializando AuthManager global: {e}")
    auth_manager = None
    
