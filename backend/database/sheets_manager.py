"""
Gestor de Google Sheets para MedConnect
Maneja todas las operaciones CRUD con la base de datos en Google Sheets
"""
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any
from config import Config, SHEETS_STANDARD_CONFIG
import os
import uuid

logger = logging.getLogger(__name__)

# Definir los encabezados de las hojas de cálculo
HEADERS_ATENCIONES = SHEETS_STANDARD_CONFIG.get('Atenciones_Medicas', [])
HEADERS_ARCHIVOS = SHEETS_STANDARD_CONFIG.get('Archivos_Adjuntos', [])

class SheetsManager:
    def __init__(self):
        """Inicializa la conexión con Google Sheets"""
        self.gc = None
        self.spreadsheet = None
        self.connect()
    
    def connect(self):
        """Establece conexión con Google Sheets"""
        try:
            # Configurar credenciales
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Verificar si tenemos credenciales en variable de entorno (Railway)
            if os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'):
                import json
                service_account_info = json.loads(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'))
                creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
                logger.info("✅ Credenciales cargadas desde GOOGLE_SERVICE_ACCOUNT_JSON")
            elif Config.GOOGLE_CREDENTIALS_FILE and os.path.exists(Config.GOOGLE_CREDENTIALS_FILE):
                # Usar archivo de credenciales local
                creds = Credentials.from_service_account_file(
                    Config.GOOGLE_CREDENTIALS_FILE, 
                    scopes=scopes
                )
                logger.info("✅ Credenciales cargadas desde archivo local")
            else:
                raise Exception("❌ No se encontraron credenciales de Google Sheets")
            
            self.gc = gspread.authorize(creds)
            self.spreadsheet = self.gc.open_by_key(Config.GOOGLE_SHEETS_ID)
            
            logger.info("✅ Conexión exitosa con Google Sheets")
            
        except Exception as e:
            logger.error(f"❌ Error conectando con Google Sheets: {e}")
            raise
    
    def get_worksheet(self, sheet_name: str):
        """Obtiene una hoja específica del spreadsheet"""
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            # Si no existe, la creamos
            return self.create_worksheet(sheet_name)
    
    def create_worksheet(self, sheet_name: str):
        """Crea una nueva hoja con headers según el tipo"""
        headers = self.get_sheet_headers(sheet_name)
        worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(headers))
        
        # Agregar headers
        worksheet.append_row(headers)
        
        logger.info(f"Hoja '{sheet_name}' creada exitosamente")
        return worksheet
    
    def get_sheet_headers(self, sheet_name: str) -> List[str]:
        """Define los headers para cada tipo de hoja usando configuración estándar"""
        return SHEETS_STANDARD_CONFIG.get(sheet_name, ['id', 'data', 'timestamp'])
    
    # CRUD Operations para Usuarios
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Crea un nuevo usuario en la base de datos"""
        try:
            worksheet = self.get_worksheet('Usuarios')
            
            # Generar ID único
            user_id = f"USR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                user_id,
                user_data.get('telegram_id', ''),
                user_data.get('nombre', ''),
                user_data.get('apellido', ''),
                user_data.get('edad', ''),
                user_data.get('rut', ''),
                user_data.get('telefono', ''),
                user_data.get('email', ''),
                user_data.get('direccion', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'activo',
                'freemium'
            ]
            
            worksheet.append_row(row_data)
            
            logger.info(f"Usuario {user_id} creado exitosamente")
            return user_id
            
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            raise
    
    def get_user_by_telegram_id(self, telegram_id: str) -> Optional[Dict[str, Any]]:
        """Busca un usuario por su Telegram ID"""
        try:
            worksheet = self.get_worksheet('Usuarios')
            records = worksheet.get_all_records()
            
            for record in records:
                if str(record.get('telegram_id')) == str(telegram_id):
                    return record
            
            return None
            
        except Exception as e:
            logger.error(f"Error buscando usuario: {e}")
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Actualiza los datos de un usuario"""
        try:
            worksheet = self.get_worksheet('Usuarios')
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, start=2):  # Start from row 2 (after headers)
                if record.get('user_id') == user_id:
                    # Actualizar campos específicos
                    for key, value in update_data.items():
                        if key in record:
                            col_index = list(record.keys()).index(key) + 1
                            worksheet.update_cell(i, col_index, value)
                    
                    logger.info(f"Usuario {user_id} actualizado exitosamente")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error actualizando usuario: {e}")
            return False
    
    # CRUD Operations para Atenciones Médicas
    def create_atencion(self, atencion_data: Dict[str, Any]) -> str:
        """Registra una nueva atención médica"""
        try:
            worksheet = self.get_worksheet('Atenciones_Medicas')
            
            # Generar ID único
            atencion_id = f"ATN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                atencion_id,
                atencion_data.get('user_id', ''),
                atencion_data.get('fecha', ''),
                atencion_data.get('hora', ''),
                atencion_data.get('tipo_atencion', ''),
                atencion_data.get('especialidad', ''),
                atencion_data.get('profesional', ''),
                atencion_data.get('centro_salud', ''),
                atencion_data.get('diagnostico', ''),
                atencion_data.get('tratamiento', ''),
                atencion_data.get('observaciones', ''),
                atencion_data.get('proxima_cita', ''),
                'registrada'
            ]
            
            worksheet.append_row(row_data)
            
            logger.info(f"Atención {atencion_id} registrada exitosamente")
            return atencion_id
            
        except Exception as e:
            logger.error(f"Error registrando atención: {e}")
            raise
    
    def get_user_atenciones(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene todas las atenciones de un usuario"""
        try:
            worksheet = self.get_worksheet('Atenciones_Medicas')
            records = worksheet.get_all_records()
            
            user_atenciones = [
                record for record in records 
                if record.get('user_id') == user_id
            ]
            
            # Ordenar por fecha más reciente
            user_atenciones.sort(
                key=lambda x: datetime.strptime(x.get('fecha', '1900-01-01'), '%Y-%m-%d'),
                reverse=True
            )
            
            return user_atenciones
            
        except Exception as e:
            logger.error(f"Error obteniendo atenciones: {e}")
            return []
    
    # CRUD Operations para Medicamentos
    def create_medicamento(self, medicamento_data: Dict[str, Any]) -> str:
        """Registra un nuevo medicamento"""
        try:
            worksheet = self.get_worksheet('Medicamentos')
            
            # Generar ID único
            medicamento_id = f"MED_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                medicamento_id,
                medicamento_data.get('user_id', ''),
                medicamento_data.get('atencion_id', ''),
                medicamento_data.get('nombre_medicamento', ''),
                medicamento_data.get('dosis', ''),
                medicamento_data.get('frecuencia', ''),
                medicamento_data.get('duracion', ''),
                medicamento_data.get('indicaciones', ''),
                medicamento_data.get('fecha_inicio', ''),
                medicamento_data.get('fecha_fin', ''),
                'activo'
            ]
            
            worksheet.append_row(row_data)
            
            logger.info(f"Medicamento {medicamento_id} registrado exitosamente")
            return medicamento_id
            
        except Exception as e:
            logger.error(f"Error registrando medicamento: {e}")
            raise
    
    def get_user_medicamentos_activos(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene los medicamentos activos de un usuario"""
        try:
            worksheet = self.get_worksheet('Medicamentos')
            records = worksheet.get_all_records()
            
            medicamentos_activos = []
            today = datetime.now().date()
            
            for record in records:
                if record.get('user_id') == user_id and record.get('estado') == 'activo':
                    # Verificar si aún está vigente
                    try:
                        fecha_fin = datetime.strptime(record.get('fecha_fin', ''), '%Y-%m-%d').date()
                        if fecha_fin >= today:
                            medicamentos_activos.append(record)
                    except:
                        # Si no hay fecha fin válida, asumir que está activo
                        medicamentos_activos.append(record)
            
            return medicamentos_activos
            
        except Exception as e:
            logger.error(f"Error obteniendo medicamentos: {e}")
            return []
    
    # CRUD Operations para Exámenes
    def create_examen(self, examen_data: Dict[str, Any]) -> str:
        """Registra un nuevo examen"""
        try:
            worksheet = self.get_worksheet('Examenes')
            
            # Generar ID único
            examen_id = f"EXM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                examen_id,
                examen_data.get('user_id', ''),
                examen_data.get('atencion_id', ''),
                examen_data.get('tipo_examen', ''),
                examen_data.get('nombre_examen', ''),
                examen_data.get('fecha_solicitud', ''),
                examen_data.get('fecha_realizacion', ''),
                examen_data.get('resultado', ''),
                examen_data.get('archivo_url', ''),
                examen_data.get('observaciones', ''),
                'pendiente'
            ]
            
            worksheet.append_row(row_data)
            
            logger.info(f"Examen {examen_id} registrado exitosamente")
            return examen_id
            
        except Exception as e:
            logger.error(f"Error registrando examen: {e}")
            raise
    
    # Operaciones para Familiares
    def add_familiar_autorizado(self, familiar_data: Dict[str, Any]) -> str:
        """Agrega un familiar autorizado"""
        try:
            worksheet = self.get_worksheet('Familiares_Autorizados')
            
            # Generar ID único
            familiar_id = f"FAM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                familiar_id,
                familiar_data.get('user_id', ''),
                familiar_data.get('nombre_familiar', ''),
                familiar_data.get('parentesco', ''),
                familiar_data.get('telefono', ''),
                familiar_data.get('email', ''),
                familiar_data.get('telegram_id', ''),
                familiar_data.get('permisos', 'lectura'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'activo',
                familiar_data.get('notificaciones', 'true')
            ]
            
            worksheet.append_row(row_data)
            
            logger.info(f"Familiar {familiar_id} autorizado exitosamente")
            return familiar_id
            
        except Exception as e:
            logger.error(f"Error autorizando familiar: {e}")
            raise
    
    def get_familiares_autorizados(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene los familiares autorizados de un usuario"""
        try:
            worksheet = self.get_worksheet('Familiares_Autorizados')
            records = worksheet.get_all_records()
            
            familiares = [
                record for record in records 
                if record.get('user_id') == user_id and record.get('estado') == 'activo'
            ]
            
            return familiares
            
        except Exception as e:
            logger.error(f"Error obteniendo familiares: {e}")
            return []
    
    # Logging
    def log_action(self, user_id: str, action: str, detail: str, ip_address: str = "", result: str = "success"):
        """Registra una acción en el log"""
        try:
            worksheet = self.get_worksheet('Logs_Acceso')
            
            log_id = f"LOG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                log_id,
                user_id,
                action,
                detail,
                ip_address,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                result
            ]
            
            worksheet.append_row(row_data)
            
        except Exception as e:
            logger.error(f"Error registrando log: {e}")
    
    # Métodos de utilidad
    def get_user_summary(self, user_id: str) -> Dict[str, Any]:
        """Obtiene un resumen completo del usuario"""
        try:
            user = self.get_user_by_telegram_id(user_id)
            if not user:
                return {}
            
            atenciones = self.get_user_atenciones(user.get('user_id', ''))
            medicamentos = self.get_user_medicamentos_activos(user.get('user_id', ''))
            familiares = self.get_familiares_autorizados(user.get('user_id', ''))
            
            return {
                'usuario': user,
                'total_atenciones': len(atenciones),
                'atenciones_recientes': atenciones[:5],
                'medicamentos_activos': len(medicamentos),
                'medicamentos': medicamentos,
                'familiares_autorizados': len(familiares)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen del usuario: {e}")
            return {}

    # Métodos para gestión familiar avanzada
    def authorize_family_member(self, user_id: str, family_data: Dict[str, Any]) -> str:
        """Autoriza a un familiar con permisos específicos"""
        try:
            worksheet = self.get_worksheet('Familiares_Autorizados')
            
            # Generar ID único
            familiar_id = f"FAM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                familiar_id,
                user_id,
                family_data.get('nombre_familiar', ''),
                family_data.get('parentesco', ''),
                family_data.get('telefono', ''),
                family_data.get('email', ''),
                                 family_data.get('telegram_id', ''),  # Nuevo campo para telegram_id del familiar
                 family_data.get('permisos', 'lectura'),  # lectura, escritura, admin
                 datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 'activo',
                 family_data.get('notificaciones', 'true')  # Recibir notificaciones
            ]
            
            worksheet.append_row(row_data)
            
            logger.info(f"Familiar {familiar_id} autorizado exitosamente")
            return familiar_id
            
        except Exception as e:
            logger.error(f"Error autorizando familiar: {e}")
            raise

    def get_managed_users(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene usuarios que puede gestionar el usuario actual"""
        try:
            worksheet = self.get_worksheet('Familiares_Autorizados')
            records = worksheet.get_all_records()
            
            managed_users = []
            
            for record in records:
                if (record.get('telegram_id') == str(user_id) and 
                    record.get('estado') == 'activo' and
                    record.get('permisos') in ['escritura', 'admin']):
                    
                    # Obtener datos del usuario principal
                    main_user = self.get_user_by_id(record.get('user_id'))
                    if main_user:
                        managed_users.append({
                            'id': record.get('user_id'),
                            'nombre': main_user.get('nombre', ''),
                            'apellido': main_user.get('apellido', ''),
                            'parentesco': record.get('parentesco', ''),
                            'permisos': record.get('permisos', '')
                        })
            
            return managed_users
            
        except Exception as e:
            logger.error(f"Error obteniendo usuarios gestionados: {e}")
            return []

    def check_family_permission(self, user_id: str, target_user_id: str) -> bool:
        """Verifica si un usuario tiene permisos para gestionar otro usuario"""
        try:
            # Un usuario siempre puede gestionar su propia información
            if user_id == target_user_id:
                return True
                
            worksheet = self.get_worksheet('Familiares_Autorizados')
            records = worksheet.get_all_records()
            
            for record in records:
                if (record.get('user_id') == target_user_id and 
                    record.get('telegram_id') == str(user_id) and
                    record.get('estado') == 'activo'):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando permisos familiares: {e}")
            return False

    def get_family_for_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene familiares que deben recibir notificaciones"""
        try:
            worksheet = self.get_worksheet('Familiares_Autorizados')
            records = worksheet.get_all_records()
            
            family_for_notifications = []
            
            for record in records:
                if (record.get('user_id') == user_id and 
                    record.get('estado') == 'activo' and
                    record.get('notificaciones') == 'true' and
                    record.get('telegram_id')):
                    
                    family_for_notifications.append({
                        'telegram_id': record.get('telegram_id'),
                        'nombre_familiar': record.get('nombre_familiar'),
                        'parentesco': record.get('parentesco')
                    })
            
            return family_for_notifications
            
        except Exception as e:
            logger.error(f"Error obteniendo familia para notificaciones: {e}")
            return []

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Busca un usuario por su ID interno"""
        try:
            worksheet = self.get_worksheet('Usuarios')
            records = worksheet.get_all_records()
            
            for record in records:
                if (record.get('id') == user_id or 
                    record.get('user_id') == user_id):
                    return record
            
            return None
            
        except Exception as e:
            logger.error(f"Error buscando usuario por ID: {e}")
            return None

    def get_medical_summary(self, user_id: str) -> Dict[str, Any]:
        """Obtiene resumen médico completo de un usuario"""
        try:
            atenciones = self.get_user_atenciones(user_id)
            medicamentos = self.get_user_medicamentos_activos(user_id)
            examenes = self.get_user_examenes(user_id)
            
            return {
                'total_consultas': len(atenciones),
                'consultas_recientes': atenciones[:3],
                'medicamentos_activos': len(medicamentos),
                'medicamentos': medicamentos,
                'total_examenes': len(examenes),
                'examenes_recientes': examenes[:3]
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen médico: {e}")
            return {}

    def get_user_examenes(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene exámenes de un usuario"""
        try:
            worksheet = self.get_worksheet('Examenes')
            records = worksheet.get_all_records()
            
            user_examenes = [
                record for record in records 
                if record.get('user_id') == user_id
            ]
            
            # Ordenar por fecha más reciente
            user_examenes.sort(
                key=lambda x: datetime.strptime(x.get('fecha_realizacion', '1900-01-01'), '%Y-%m-%d') if x.get('fecha_realizacion') else datetime.min,
                reverse=True
            )
            
            return user_examenes
            
        except Exception as e:
            logger.error(f"Error obteniendo exámenes: {e}")
            return []

    # Gestión de recordatorios y notificaciones
    def create_reminder(self, reminder_data: Dict[str, Any]) -> str:
        """Crea un recordatorio/notificación"""
        try:
            worksheet = self.get_worksheet('Recordatorios')
            
            # Generar ID único
            reminder_id = f"REM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                reminder_id,
                reminder_data.get('user_id', ''),
                reminder_data.get('tipo', ''),  # medicamento, cita, general
                reminder_data.get('titulo', ''),
                reminder_data.get('mensaje', ''),
                reminder_data.get('fecha_programada', ''),
                reminder_data.get('hora_programada', ''),
                reminder_data.get('frecuencia', 'unica'),  # unica, diaria, semanal
                reminder_data.get('notificar_familiares', 'false'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'activo'
            ]
            
            worksheet.append_row(row_data)
            
            logger.info(f"Recordatorio {reminder_id} creado exitosamente")
            return reminder_id
            
        except Exception as e:
            logger.error(f"Error creando recordatorio: {e}")
            raise

    def get_user_active_reminders(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene recordatorios activos de un usuario"""
        try:
            worksheet = self.get_worksheet('Recordatorios')
            records = worksheet.get_all_records()
            
            active_reminders = []
            today = datetime.now().date()
            
            for record in records:
                if (record.get('user_id') == user_id and 
                    record.get('estado') == 'activo'):
                    
                    # Verificar si el recordatorio aún está vigente
                    try:
                        fecha_programada = datetime.strptime(record.get('fecha_programada', ''), '%Y-%m-%d').date()
                        if fecha_programada >= today:
                            active_reminders.append(record)
                    except:
                        # Si no hay fecha válida, incluir el recordatorio
                        active_reminders.append(record)
            
            return active_reminders
            
        except Exception as e:
            logger.error(f"Error obteniendo recordatorios activos: {e}")
            return []

    def update_sheet_headers(self, sheet_name: str, additional_headers: List[str]):
        """Actualiza headers de una hoja agregando campos faltantes"""
        try:
            worksheet = self.get_worksheet(sheet_name)
            current_headers = worksheet.row_values(1)
            
            new_headers = []
            for header in additional_headers:
                if header not in current_headers:
                    new_headers.append(header)
            
            if new_headers:
                # Agregar nuevos headers
                updated_headers = current_headers + new_headers
                worksheet.clear()
                worksheet.append_row(updated_headers)
                logger.info(f"Headers actualizados en {sheet_name}: {new_headers}")
            
        except Exception as e:
            logger.error(f"Error actualizando headers de {sheet_name}: {e}")

    def create_archivo_adjunto(self, archivo_data: Dict[str, Any]) -> str:
        """
        Crea un nuevo registro de archivo adjunto
        """
        try:
            # Obtener o crear la hoja de archivos adjuntos
            try:
                worksheet = self.spreadsheet.worksheet('Archivos_Adjuntos')
            except Exception:
                # Si no existe, crear la hoja con headers
                worksheet = self.spreadsheet.add_worksheet(title='Archivos_Adjuntos', rows=1000, cols=8)
                headers = [
                    'archivo_id',
                    'atencion_id',
                    'nombre_archivo',
                    'tipo_archivo',
                    'ruta_archivo',
                    'fecha_subida',
                    'tamaño',
                    'estado'
                ]
                worksheet.append_row(headers)

            # Generar ID único para el archivo
            archivo_id = f"FILE_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

            # Preparar datos para insertar
            nuevo_archivo = [
                archivo_id,
                archivo_data.get('atencion_id', ''),
                archivo_data.get('nombre_archivo', ''),
                archivo_data.get('tipo_archivo', ''),
                archivo_data.get('ruta_archivo', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                archivo_data.get('tamaño', 0),
                'activo'
            ]

            # Insertar en Google Sheets
            worksheet.append_row(nuevo_archivo)

            # Actualizar el campo tiene_archivos en la atención
            self.update_atencion_archivos_status(archivo_data.get('atencion_id', ''))

            return archivo_id

        except Exception as e:
            logger.error(f"Error creando archivo adjunto: {e}")
            raise

    def update_atencion_archivos_status(self, atencion_id: str) -> None:
        """
        Actualiza el estado de archivos de una atención
        """
        try:
            worksheet = self.spreadsheet.worksheet('Atenciones_Medicas')
            cell = worksheet.find(atencion_id)
            if cell:
                # Actualizar la columna tiene_archivos (asumiendo que es la columna 16)
                worksheet.update_cell(cell.row, 16, 'Sí')
        except Exception as e:
            logger.error(f"Error actualizando estado de archivos: {e}")
            raise

    def get_archivos_atencion(self, atencion_id):
        """
        Obtiene los archivos adjuntos de una atención
        """
        try:
            # Verificar si la hoja existe
            try:
                worksheet = self.spreadsheet.worksheet('Archivos_Adjuntos')
            except Exception as e:
                logger.warning(f"Hoja Archivos_Adjuntos no encontrada: {e}")
                return []

            # Obtener registros
            try:
                records = worksheet.get_all_records()
            except Exception as e:
                logger.error(f"Error obteniendo registros: {e}")
                return []
            
            # Filtrar archivos de la atención
            archivos = []
            for record in records:
                try:
                    if str(record.get('atencion_id', '')) == str(atencion_id) and record.get('estado', '') == 'activo':
                        archivos.append({
                            'archivo_id': record.get('archivo_id', ''),
                            'nombre_archivo': record.get('nombre_archivo', ''),
                            'tipo_archivo': record.get('tipo_archivo', ''),
                            'ruta_archivo': record.get('ruta_archivo', ''),
                            'fecha_subida': record.get('fecha_subida', ''),
                            'tamaño': record.get('tamaño', 0)
                        })
                except Exception as e:
                    logger.error(f"Error procesando registro de archivo: {e}")
                    continue
            
            return archivos
            
        except Exception as e:
            logger.error(f"Error en get_archivos_atencion: {e}")
            return []

    def get_archivo_by_id(self, archivo_id):
        """
        Obtiene la información de un archivo por su ID
        """
        try:
            worksheet = self.spreadsheet.worksheet('Archivos_Adjuntos')
            records = worksheet.get_all_records()
            
            for record in records:
                if str(record.get('archivo_id', '')) == str(archivo_id):
                    return {
                        'archivo_id': record.get('archivo_id', ''),
                        'atencion_id': record.get('atencion_id', ''),
                        'nombre_archivo': record.get('nombre_archivo', ''),
                        'tipo_archivo': record.get('tipo_archivo', ''),
                        'ruta_archivo': record.get('ruta_archivo', ''),
                        'fecha_subida': record.get('fecha_subida', ''),
                        'tamaño': record.get('tamaño', 0),
                        'estado': record.get('estado', '')
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo archivo por ID: {e}")
            return None

    def get_atencion_by_id(self, atencion_id):
        """
        Obtiene una atención médica por su ID
        """
        try:
            # Verificar si la hoja existe
            try:
                worksheet = self.spreadsheet.worksheet('Atenciones_Medicas')
            except Exception as e:
                logger.error(f"Hoja Atenciones_Medicas no encontrada: {e}")
                return None

            # Obtener registros
            try:
                records = worksheet.get_all_records()
            except Exception as e:
                logger.error(f"Error obteniendo registros: {e}")
                return None

            # Buscar la atención
            for record in records:
                try:
                    if str(record.get('atencion_id', '')) == str(atencion_id):
                        return {
                            'atencion_id': record.get('atencion_id', ''),
                            'paciente_id': record.get('paciente_id', ''),
                            'profesional_id': record.get('profesional_id', ''),
                            'fecha_atencion': record.get('fecha_atencion', ''),
                            'hora_atencion': record.get('hora_atencion', ''),
                            'motivo': record.get('motivo', ''),
                            'diagnostico': record.get('diagnostico', ''),
                            'tratamiento': record.get('tratamiento', ''),
                            'notas': record.get('notas', ''),
                            'estado': record.get('estado', ''),
                            'tiene_archivos': record.get('tiene_archivos', False)
                        }
                except Exception as e:
                    logger.error(f"Error procesando registro de atención: {e}")
                    continue

            return None

        except Exception as e:
            logger.error(f"Error en get_atencion_by_id: {e}")
            return None

    def registrar_atencion(self, data):
        """Registra una nueva atención médica en la hoja de cálculo."""
        try:
            worksheet = self.get_or_create_worksheet('Atenciones_Medicas', HEADERS_ATENCIONES)
            
            atencion_id = f"ATN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            nueva_fila = {
                'atencion_id': atencion_id,
                'profesional_id': data.get('profesional_id', ''),
                'profesional_nombre': data.get('profesional_nombre', ''),
                'paciente_id': data.get('pacienteId', ''),
                'paciente_nombre': data.get('paciente_nombre', ''),
                'paciente_rut': data.get('paciente_rut', ''),
                'paciente_edad': data.get('paciente_edad', ''),
                'fecha_hora': data.get('fecha_hora', ''),
                'tipo_atencion': data.get('tipo_atencion', ''),
                'motivo_consulta': data.get('motivo_consulta', ''),
                'diagnostico': data.get('diagnostico', ''),
                'tratamiento': data.get('tratamiento', ''),
                'observaciones': data.get('observaciones', ''),
                'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'estado': data.get('estado', 'completada'),
                'requiere_seguimiento': data.get('requiere_seguimiento', 'No'),
                'tiene_archivos': data.get('tiene_archivos', 'No')
            }
            
            worksheet.append_row(list(nueva_fila.values()))
            logger.info(f"✅ Atención registrada en Sheets: {atencion_id}")
            
            # Si se proporcionaron datos del paciente, crear/actualizar registro en Pacientes_Profesional
            if (data.get('paciente_nombre') and data.get('paciente_rut') and 
                data.get('profesional_id') and not data.get('pacienteId')):
                
                logger.info("📝 Creando nuevo paciente en Pacientes_Profesional...")
                try:
                    # Crear registro del paciente
                    paciente_id = self._crear_paciente_desde_atencion(data, atencion_id)
                    
                    # Actualizar la atención con el paciente_id generado
                    nueva_fila['paciente_id'] = paciente_id
                    
                    # Actualizar la fila en la hoja (buscar por atencion_id y actualizar)
                    records = worksheet.get_all_records()
                    for i, record in enumerate(records):
                        if record.get('atencion_id') == atencion_id:
                            worksheet.update(f'D{i+2}', [[paciente_id]])  # Columna D es paciente_id
                            break
                    
                    logger.info(f"✅ Paciente {paciente_id} creado y vinculado a atención {atencion_id}")
                    
                except Exception as e:
                    logger.error(f"❌ Error creando paciente desde atención: {e}")
                    # La atención ya está registrada, continuamos
            
            return atencion_id, nueva_fila
            
        except Exception as e:
            logger.error(f"Error en registrar_atencion: {e}")
            raise

    def _crear_paciente_desde_atencion(self, data, atencion_id):
        """Crea un nuevo paciente en la hoja Pacientes_Profesional desde los datos de una atención."""
        try:
            # Headers para Pacientes_Profesional
            headers_pacientes = ['paciente_id', 'profesional_id', 'nombre_completo', 'rut', 'edad',
                               'fecha_nacimiento', 'genero', 'telefono', 'email', 'direccion',
                               'antecedentes_medicos', 'fecha_primera_consulta', 'ultima_consulta',
                               'num_atenciones', 'estado_relacion', 'fecha_registro', 'notas']
            
            worksheet = self.get_or_create_worksheet('Pacientes_Profesional', headers_pacientes)
            
            # Verificar si el paciente ya existe para este profesional
            records = worksheet.get_all_records()
            for i, record in enumerate(records):
                if (str(record.get('profesional_id', '')) == str(data.get('profesional_id', '')) and 
                    record.get('rut', '').strip().lower() == data.get('paciente_rut', '').strip().lower()):
                    logger.info(f"📋 Paciente con RUT {data.get('paciente_rut')} ya existe para profesional {data.get('profesional_id')}")
                    
                    # Actualizar contador de atenciones y última consulta
                    try:
                        num_atenciones = int(record.get('num_atenciones', 0)) + 1
                        worksheet.update(f'N{i+2}', [[num_atenciones]])  # Columna N es num_atenciones
                        worksheet.update(f'M{i+2}', [[data.get('fecha_hora', '')]])  # Columna M es ultima_consulta
                        logger.info(f"✅ Actualizado contador de atenciones para paciente: {num_atenciones}")
                    except Exception as e:
                        logger.error(f"❌ Error actualizando contador de atenciones: {e}")
                    
                    return record.get('paciente_id', '')
            
            # Generar ID único para el paciente
            paciente_id = f"PAC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Preparar datos del paciente
            nuevo_paciente = [
                paciente_id,
                data.get('profesional_id', ''),
                data.get('paciente_nombre', ''),
                data.get('paciente_rut', ''),
                data.get('paciente_edad', ''),
                data.get('paciente_fecha_nacimiento', ''),
                data.get('paciente_genero', ''),
                data.get('paciente_telefono', ''),
                data.get('paciente_email', ''),
                data.get('paciente_direccion', ''),
                data.get('paciente_antecedentes', ''),
                data.get('fecha_hora', ''),  # fecha_primera_consulta
                data.get('fecha_hora', ''),  # ultima_consulta
                1,  # num_atenciones (esta es la primera)
                'activo',  # estado_relacion
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                f'Paciente creado automáticamente desde atención {atencion_id}'
            ]
            
            # Insertar en Google Sheets
            worksheet.append_row(nuevo_paciente)
            logger.info(f"✅ Paciente {paciente_id} creado automáticamente desde atención")
            
            return paciente_id
            
        except Exception as e:
            logger.error(f"Error creando paciente desde atención: {e}")
            raise

    def registrar_archivo_adjunto(self, data):
        """Registra un nuevo archivo adjunto en la hoja de cálculo."""
        try:
            worksheet = self.get_or_create_worksheet('Archivos_Adjuntos', HEADERS_ARCHIVOS)
            
            archivo_id = f"FILE_{uuid.uuid4().hex[:12].upper()}"
            
            nueva_fila = [
                archivo_id,
                data.get('atencion_id'),
                data.get('nombre_archivo'),
                data.get('tipo_archivo'),
                data.get('ruta_archivo'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                data.get('tamaño'),
                'activo' # estado
            ]
            
            worksheet.append_row(nueva_fila)
            logger.info(f"✅ Archivo adjunto registrado en Sheets: {archivo_id} para atención {data.get('atencion_id')}")
            
            return archivo_id
            
        except Exception as e:
            logger.error(f"Error en registrar_archivo_adjunto: {e}")
            raise

    def get_or_create_worksheet(self, title, headers):
        """
        Obtiene una hoja de cálculo por su título. Si no existe, la crea con los encabezados especificados.
        """
        try:
            worksheet = self.spreadsheet.worksheet(title)
            logger.info(f"Hoja '{title}' encontrada.")
            return worksheet
        except gspread.exceptions.WorksheetNotFound:
            logger.warning(f"Hoja '{title}' no encontrada. Creando una nueva...")
            worksheet = self.spreadsheet.add_worksheet(title=title, rows=1000, cols=len(headers))
            worksheet.append_row(headers)
            logger.info(f"✅ Hoja '{title}' creada con éxito.")
            return worksheet
        except Exception as e:
            logger.error(f"Error al obtener o crear la hoja '{title}': {e}")
            raise

    def get_all_records(self, sheet_name):
        """Obtiene todos los registros de una hoja de cálculo."""
        try:
            worksheet = self.get_worksheet(sheet_name)
            return worksheet.get_all_records()
        except Exception as e:
            logger.error(f"Error obteniendo registros de {sheet_name}: {e}")
            return []

# Instancia global del gestor
sheets_db = SheetsManager() 