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
import json
import time

logger = logging.getLogger(__name__)

# Definir los encabezados de las hojas de cálculo
HEADERS_ATENCIONES = SHEETS_STANDARD_CONFIG.get("Atenciones_Medicas", [])
HEADERS_ARCHIVOS = SHEETS_STANDARD_CONFIG.get("Archivos_Adjuntos", [])


class SheetsManager:
    def __init__(self):
        """Inicializa la conexión con Google Sheets"""
        self.gc = None
        self.spreadsheet = None
        self.last_request_time = 0
        self.request_count = 0
        self.cache = {}
        self.cache_duration = 60  # segundos - aumentar cache para reducir requests
        self.max_requests_per_minute = 45  # Límite más conservador para evitar 429
        self.use_fallback = False  # Nuevo atributo para manejar el fallback
        self.connect()
    
    def _rate_limit(self):
        """Implementa rate limiting mejorado para evitar exceder límites de API"""
        current_time = time.time()
        
        # Resetear contador si ha pasado más de 1 minuto
        if current_time - self.last_request_time > 60:
            self.request_count = 0
            self.last_request_time = current_time
        
        # Límite más conservador para evitar 429
        if self.request_count >= self.max_requests_per_minute:
            wait_time = 60 - (current_time - self.last_request_time)
            if wait_time > 0:
                logger.warning(
                    f"⚠️ Rate limit alcanzado, esperando {wait_time:.2f} segundos"
                )
                time.sleep(wait_time)
                self.request_count = 0
                self.last_request_time = time.time()
        
        self.request_count += 1
        
        # Logging para monitoreo
        try:
            from api_monitoring import log_api_request

            log_api_request("sheets.values.get", success=True)
        except Exception as e:
            logger.debug(f"No se pudo registrar request: {e}")
    
    def _get_cache_key(self, method, *args):
        """Genera una clave única para el cache"""
        return f"{method}_{'_'.join(str(arg) for arg in args)}"
    
    def _get_from_cache(self, cache_key):
        """Obtiene datos del cache si están disponibles y no han expirado"""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                logger.debug(f"📋 Datos obtenidos del cache: {cache_key}")
                return cached_data
            else:
                # Eliminar cache expirado
                del self.cache[cache_key]
        return None
    
    def _set_cache(self, cache_key, data):
        """Guarda datos en el cache"""
        self.cache[cache_key] = (data, time.time())
        logger.debug(f"💾 Datos guardados en cache: {cache_key}")
        
        # Limpiar cache si es muy grande (más de 100 entradas)
        if len(self.cache) > 100:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
    
    def connect(self):
        """Conectar con Google Sheets"""
        try:
            # Rate limiting antes de conectar
            self._rate_limit()
            
            # Configurar credenciales
            if os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"):
                credentials_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")

                # Verificar si es un path en lugar de JSON
                if credentials_json.startswith("./") or credentials_json.startswith(
                    "/"
                ):
                    logger.info(f"📁 Detectado path de archivo: {credentials_json}")
                    if os.path.exists(credentials_json):
                        with open(credentials_json, "r") as f:
                            service_account_info = json.load(f)
                        logger.info(
                            "✅ Credenciales cargadas desde archivo especificado"
                        )
                    else:
                        logger.error(f"❌ Archivo no encontrado: {credentials_json}")
                        logger.warning("⚠️ Usando sistema de fallback")
                        self.use_fallback = True
                        return True
                else:
                    # Intentar parsear como JSON
                    try:
                        service_account_info = json.loads(credentials_json)
                        logger.info(
                            "✅ Credenciales cargadas desde GOOGLE_SERVICE_ACCOUNT_JSON"
                        )
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ Error parseando JSON: {e}")
                        logger.warning("⚠️ Usando sistema de fallback")
                        self.use_fallback = True
                        return True

                # Agregar scopes específicos para Google Sheets
                scopes = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ]
                creds = Credentials.from_service_account_info(
                    service_account_info, scopes=scopes
                )
            else:
                logger.error("❌ GOOGLE_SERVICE_ACCOUNT_JSON no configurado")
                logger.warning("⚠️ Usando sistema de fallback")
                self.use_fallback = True
                return True
            
            # Crear cliente con retry automático
            self.gc = gspread.authorize(creds)
            
            # Intentar conectar con retry
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    self.spreadsheet = self.gc.open_by_key(Config.GOOGLE_SHEETS_ID)
                    
                    # Verificar que el objeto spreadsheet esté disponible
                    if not self.spreadsheet:
                        logger.error("❌ El objeto spreadsheet no está disponible")
                        self.use_fallback = True
                        return True
                    
                    logger.info("✅ Conexión exitosa con Google Sheets")
                    return True
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        wait_time = retry_delay * (2**attempt)  # Exponential backoff
                        logger.warning(
                            f"⚠️ Rate limit detectado, esperando {wait_time} segundos (intento {attempt + 1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"❌ Error conectando con Google Sheets: {e}")
                        logger.warning("⚠️ Usando sistema de fallback")
                        self.use_fallback = True
                        return True
            
            logger.error("❌ No se pudo conectar después de múltiples intentos")
            logger.warning("⚠️ Usando sistema de fallback")
            self.use_fallback = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en connect(): {e}")
            logger.warning("⚠️ Usando sistema de fallback")
            self.use_fallback = True
            return True
    
    def get_worksheet(self, sheet_name: str):
        """Obtiene una hoja específica del spreadsheet con cache"""
        try:
            # Rate limiting
            self._rate_limit()
            
            # Intentar obtener del cache
            cache_key = self._get_cache_key("worksheet", sheet_name)
            cached_worksheet = self._get_from_cache(cache_key)
            if cached_worksheet:
                return cached_worksheet
            
            # Si no está en cache, obtener de la API con retry
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    worksheet = self.spreadsheet.worksheet(sheet_name)
                    
                    # Guardar en cache
                    self._set_cache(cache_key, worksheet)
                    
                    return worksheet
                    
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        wait_time = retry_delay * (2**attempt)  # Exponential backoff
                        logger.warning(
                            f"⚠️ Rate limit en get_worksheet, esperando {wait_time}s (intento {attempt + 1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                        
                        # Logging para monitoreo
                        try:
                            from api_monitoring import log_api_request

                            log_api_request(
                                "sheets.values.get", success=False, error_type="429"
                            )
                        except Exception:
                            pass
                    else:
                        raise e
            
            logger.error(
                f"❌ No se pudo obtener worksheet después de {max_retries} intentos"
            )
            return None
            
        except gspread.WorksheetNotFound:
            # Si no existe, la creamos
            return self.create_worksheet(sheet_name)
        except Exception as e:
            logger.error(f"❌ Error obteniendo worksheet '{sheet_name}': {e}")
            return None
    
    def create_worksheet(self, sheet_name: str):
        """Crea una nueva hoja con headers según el tipo"""
        headers = self.get_sheet_headers(sheet_name)
        worksheet = self.spreadsheet.add_worksheet(
            title=sheet_name, rows=1000, cols=len(headers)
        )
        
        # Agregar headers
        worksheet.append_row(headers)
        
        logger.info(f"Hoja '{sheet_name}' creada exitosamente")
        return worksheet
    
    def get_sheet_headers(self, sheet_name: str) -> List[str]:
        """Define los headers para cada tipo de hoja usando configuración estándar"""
        return SHEETS_STANDARD_CONFIG.get(sheet_name, ["id", "data", "timestamp"])
    
    # CRUD Operations para Usuarios
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Crea un nuevo usuario en la base de datos"""
        try:
            worksheet = self.get_worksheet("Usuarios")
            
            # Generar ID único
            user_id = f"USR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                user_id,
                user_data.get("telegram_id", ""),
                user_data.get("nombre", ""),
                user_data.get("apellido", ""),
                user_data.get("edad", ""),
                user_data.get("rut", ""),
                user_data.get("telefono", ""),
                user_data.get("email", ""),
                user_data.get("direccion", ""),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "activo",
                "freemium",
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
            worksheet = self.get_worksheet("Usuarios")
            records = worksheet.get_all_records()
            
            for record in records:
                if str(record.get("telegram_id")) == str(telegram_id):
                    return record
            
            return None
            
        except Exception as e:
            logger.error(f"Error buscando usuario: {e}")
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Actualiza los datos de un usuario"""
        try:
            worksheet = self.get_worksheet("Usuarios")
            records = worksheet.get_all_records()
            
            for i, record in enumerate(
                records, start=2
            ):  # Start from row 2 (after headers)
                if record.get("user_id") == user_id:
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
            worksheet = self.get_worksheet("Atenciones_Medicas")
            
            # Generar ID único
            atencion_id = f"ATN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                atencion_id,
                atencion_data.get("user_id", ""),
                atencion_data.get("fecha", ""),
                atencion_data.get("hora", ""),
                atencion_data.get("tipo_atencion", ""),
                atencion_data.get("especialidad", ""),
                atencion_data.get("profesional", ""),
                atencion_data.get("centro_salud", ""),
                atencion_data.get("diagnostico", ""),
                atencion_data.get("tratamiento", ""),
                atencion_data.get("observaciones", ""),
                atencion_data.get("proxima_cita", ""),
                "registrada",
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
            worksheet = self.get_worksheet("Atenciones_Medicas")
            records = worksheet.get_all_records()
            
            user_atenciones = [
                record for record in records if record.get("user_id") == user_id
            ]
            
            # Ordenar por fecha más reciente
            user_atenciones.sort(
                key=lambda x: datetime.strptime(
                    x.get("fecha", "1900-01-01"), "%Y-%m-%d"
                ),
                reverse=True,
            )
            
            return user_atenciones
            
        except Exception as e:
            logger.error(f"Error obteniendo atenciones: {e}")
            return []
    
    # CRUD Operations para Medicamentos
    def create_medicamento(self, medicamento_data: Dict[str, Any]) -> str:
        """Registra un nuevo medicamento"""
        try:
            worksheet = self.get_worksheet("Medicamentos")
            
            # Generar ID único
            medicamento_id = f"MED_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                medicamento_id,
                medicamento_data.get("user_id", ""),
                medicamento_data.get("atencion_id", ""),
                medicamento_data.get("nombre_medicamento", ""),
                medicamento_data.get("dosis", ""),
                medicamento_data.get("frecuencia", ""),
                medicamento_data.get("duracion", ""),
                medicamento_data.get("indicaciones", ""),
                medicamento_data.get("fecha_inicio", ""),
                medicamento_data.get("fecha_fin", ""),
                "activo",
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
            worksheet = self.get_worksheet("Medicamentos")
            records = worksheet.get_all_records()
            
            medicamentos_activos = []
            today = datetime.now().date()
            
            for record in records:
                if (
                    record.get("user_id") == user_id
                    and record.get("estado") == "activo"
                ):
                    # Verificar si aún está vigente
                    try:
                        fecha_fin = datetime.strptime(
                            record.get("fecha_fin", ""), "%Y-%m-%d"
                        ).date()
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
            worksheet = self.get_worksheet("Examenes")
            
            # Generar ID único
            examen_id = f"EXM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                examen_id,
                examen_data.get("user_id", ""),
                examen_data.get("atencion_id", ""),
                examen_data.get("tipo_examen", ""),
                examen_data.get("nombre_examen", ""),
                examen_data.get("fecha_solicitud", ""),
                examen_data.get("fecha_realizacion", ""),
                examen_data.get("resultado", ""),
                examen_data.get("archivo_url", ""),
                examen_data.get("observaciones", ""),
                "pendiente",
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
            worksheet = self.get_worksheet("Familiares_Autorizados")
            
            # Generar ID único
            familiar_id = f"FAM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                familiar_id,
                familiar_data.get("user_id", ""),
                familiar_data.get("nombre_familiar", ""),
                familiar_data.get("parentesco", ""),
                familiar_data.get("telefono", ""),
                familiar_data.get("email", ""),
                familiar_data.get("telegram_id", ""),
                familiar_data.get("permisos", "lectura"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "activo",
                familiar_data.get("notificaciones", "true"),
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
            worksheet = self.get_worksheet("Familiares_Autorizados")
            records = worksheet.get_all_records()
            
            familiares = [
                record
                for record in records
                if record.get("user_id") == user_id and record.get("estado") == "activo"
            ]
            
            return familiares
            
        except Exception as e:
            logger.error(f"Error obteniendo familiares: {e}")
            return []
    
    # Logging
    def log_action(
        self,
        user_id: str,
        action: str,
        detail: str,
        ip_address: str = "",
        result: str = "success",
    ):
        """Registra una acción en el log"""
        try:
            worksheet = self.get_worksheet("Logs_Acceso")
            
            log_id = f"LOG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                log_id,
                user_id,
                action,
                detail,
                ip_address,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                result,
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
            
            atenciones = self.get_user_atenciones(user.get("user_id", ""))
            medicamentos = self.get_user_medicamentos_activos(user.get("user_id", ""))
            familiares = self.get_familiares_autorizados(user.get("user_id", ""))
            
            return {
                "usuario": user,
                "total_atenciones": len(atenciones),
                "atenciones_recientes": atenciones[:5],
                "medicamentos_activos": len(medicamentos),
                "medicamentos": medicamentos,
                "familiares_autorizados": len(familiares),
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen del usuario: {e}")
            return {}

    # Métodos para gestión familiar avanzada
    def authorize_family_member(self, user_id: str, family_data: Dict[str, Any]) -> str:
        """Autoriza a un familiar con permisos específicos"""
        try:
            worksheet = self.get_worksheet("Familiares_Autorizados")
            
            # Generar ID único
            familiar_id = f"FAM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                familiar_id,
                user_id,
                family_data.get("nombre_familiar", ""),
                family_data.get("parentesco", ""),
                family_data.get("telefono", ""),
                family_data.get("email", ""),
                family_data.get(
                    "telegram_id", ""
                ),  # Nuevo campo para telegram_id del familiar
                family_data.get("permisos", "lectura"),  # lectura, escritura, admin
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "activo",
                family_data.get("notificaciones", "true"),  # Recibir notificaciones
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
            worksheet = self.get_worksheet("Familiares_Autorizados")
            records = worksheet.get_all_records()
            
            managed_users = []
            
            for record in records:
                if (
                    record.get("telegram_id") == str(user_id)
                    and record.get("estado") == "activo"
                    and record.get("permisos") in ["escritura", "admin"]
                ):
                    
                    # Obtener datos del usuario principal
                    main_user = self.get_user_by_id(record.get("user_id"))
                    if main_user:
                        managed_users.append(
                            {
                                "id": record.get("user_id"),
                                "nombre": main_user.get("nombre", ""),
                                "apellido": main_user.get("apellido", ""),
                                "parentesco": record.get("parentesco", ""),
                                "permisos": record.get("permisos", ""),
                            }
                        )
            
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
                
            worksheet = self.get_worksheet("Familiares_Autorizados")
            records = worksheet.get_all_records()
            
            for record in records:
                if (
                    record.get("user_id") == target_user_id
                    and record.get("telegram_id") == str(user_id)
                    and record.get("estado") == "activo"
                ):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando permisos familiares: {e}")
            return False

    def get_family_for_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene familiares que deben recibir notificaciones"""
        try:
            worksheet = self.get_worksheet("Familiares_Autorizados")
            records = worksheet.get_all_records()
            
            family_for_notifications = []
            
            for record in records:
                if (
                    record.get("user_id") == user_id
                    and record.get("estado") == "activo"
                    and record.get("notificaciones") == "true"
                    and record.get("telegram_id")
                ):
                    
                    family_for_notifications.append(
                        {
                            "telegram_id": record.get("telegram_id"),
                            "nombre_familiar": record.get("nombre_familiar"),
                            "parentesco": record.get("parentesco"),
                        }
                    )
            
            return family_for_notifications
            
        except Exception as e:
            logger.error(f"Error obteniendo familia para notificaciones: {e}")
            return []

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Busca un usuario por su ID interno"""
        try:
            worksheet = self.get_worksheet("Usuarios")
            records = worksheet.get_all_records()
            
            for record in records:
                if record.get("id") == user_id or record.get("user_id") == user_id:
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
                "total_consultas": len(atenciones),
                "consultas_recientes": atenciones[:3],
                "medicamentos_activos": len(medicamentos),
                "medicamentos": medicamentos,
                "total_examenes": len(examenes),
                "examenes_recientes": examenes[:3],
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen médico: {e}")
            return {}

    def get_user_examenes(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene exámenes de un usuario"""
        try:
            worksheet = self.get_worksheet("Examenes")
            records = worksheet.get_all_records()
            
            user_examenes = [
                record for record in records if record.get("user_id") == user_id
            ]
            
            # Ordenar por fecha más reciente
            user_examenes.sort(
                key=lambda x: (
                    datetime.strptime(
                        x.get("fecha_realizacion", "1900-01-01"), "%Y-%m-%d"
                    )
                    if x.get("fecha_realizacion")
                    else datetime.min
                ),
                reverse=True,
            )
            
            return user_examenes
            
        except Exception as e:
            logger.error(f"Error obteniendo exámenes: {e}")
            return []

    # Gestión de recordatorios y notificaciones
    def create_reminder(self, reminder_data: Dict[str, Any]) -> str:
        """Crea un recordatorio/notificación"""
        try:
            worksheet = self.get_worksheet("Recordatorios")
            
            # Generar ID único
            reminder_id = f"REM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                reminder_id,
                reminder_data.get("user_id", ""),
                reminder_data.get("tipo", ""),  # medicamento, cita, general
                reminder_data.get("titulo", ""),
                reminder_data.get("mensaje", ""),
                reminder_data.get("fecha_programada", ""),
                reminder_data.get("hora_programada", ""),
                reminder_data.get("frecuencia", "unica"),  # unica, diaria, semanal
                reminder_data.get("notificar_familiares", "false"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "activo",
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
            worksheet = self.get_worksheet("Recordatorios")
            records = worksheet.get_all_records()
            
            active_reminders = []
            today = datetime.now().date()
            
            for record in records:
                if (
                    record.get("user_id") == user_id
                    and record.get("estado") == "activo"
                ):
                    
                    # Verificar si el recordatorio aún está vigente
                    try:
                        fecha_programada = datetime.strptime(
                            record.get("fecha_programada", ""), "%Y-%m-%d"
                        ).date()
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
                worksheet = self.spreadsheet.worksheet("Archivos_Adjuntos")
            except Exception:
                # Si no existe, crear la hoja con headers
                worksheet = self.spreadsheet.add_worksheet(
                    title="Archivos_Adjuntos", rows=1000, cols=8
                )
                headers = [
                    "archivo_id",
                    "atencion_id",
                    "nombre_archivo",
                    "tipo_archivo",
                    "ruta_archivo",
                    "fecha_subida",
                    "tamaño",
                    "estado",
                ]
                worksheet.append_row(headers)

            # Generar ID único para el archivo
            archivo_id = f"FILE_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

            # Preparar datos para insertar
            nuevo_archivo = [
                archivo_id,
                archivo_data.get("atencion_id", ""),
                archivo_data.get("nombre_archivo", ""),
                archivo_data.get("tipo_archivo", ""),
                archivo_data.get("ruta_archivo", ""),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                archivo_data.get("tamaño", 0),
                "activo",
            ]

            # Insertar en Google Sheets
            worksheet.append_row(nuevo_archivo)

            # Actualizar el campo tiene_archivos en la atención
            self.update_atencion_archivos_status(archivo_data.get("atencion_id", ""))

            return archivo_id

        except Exception as e:
            logger.error(f"Error creando archivo adjunto: {e}")
            raise

    def update_atencion_archivos_status(self, atencion_id: str) -> None:
        """
        Actualiza el estado de archivos de una atención
        """
        try:
            worksheet = self.spreadsheet.worksheet("Atenciones_Medicas")
            cell = worksheet.find(atencion_id)
            if cell:
                # Actualizar la columna tiene_archivos (asumiendo que es la columna 16)
                worksheet.update_cell(cell.row, 16, "Sí")
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
                worksheet = self.spreadsheet.worksheet("Archivos_Adjuntos")
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
                    if (
                        str(record.get("atencion_id", "")) == str(atencion_id)
                        and record.get("estado", "") == "activo"
                    ):
                        archivos.append(
                            {
                                "archivo_id": record.get("archivo_id", ""),
                                "nombre_archivo": record.get("nombre_archivo", ""),
                                "tipo_archivo": record.get("tipo_archivo", ""),
                                "ruta_archivo": record.get("ruta_archivo", ""),
                                "fecha_subida": record.get("fecha_subida", ""),
                                "tamaño": record.get("tamaño", 0),
                            }
                        )
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
            worksheet = self.spreadsheet.worksheet("Archivos_Adjuntos")
            records = worksheet.get_all_records()
            
            for record in records:
                if str(record.get("archivo_id", "")) == str(archivo_id):
                    return {
                        "archivo_id": record.get("archivo_id", ""),
                        "atencion_id": record.get("atencion_id", ""),
                        "nombre_archivo": record.get("nombre_archivo", ""),
                        "tipo_archivo": record.get("tipo_archivo", ""),
                        "ruta_archivo": record.get("ruta_archivo", ""),
                        "fecha_subida": record.get("fecha_subida", ""),
                        "tamaño": record.get("tamaño", 0),
                        "estado": record.get("estado", ""),
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
                worksheet = self.spreadsheet.worksheet("Atenciones_Medicas")
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
                    if str(record.get("atencion_id", "")) == str(atencion_id):
                        return {
                            "atencion_id": record.get("atencion_id", ""),
                            "paciente_id": record.get("paciente_id", ""),
                            "profesional_id": record.get("profesional_id", ""),
                            "fecha_atencion": record.get("fecha_atencion", ""),
                            "hora_atencion": record.get("hora_atencion", ""),
                            "motivo": record.get("motivo", ""),
                            "diagnostico": record.get("diagnostico", ""),
                            "tratamiento": record.get("tratamiento", ""),
                            "notas": record.get("notas", ""),
                            "estado": record.get("estado", ""),
                            "tiene_archivos": record.get("tiene_archivos", False),
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
            worksheet = self.get_or_create_worksheet(
                "Atenciones_Medicas", HEADERS_ATENCIONES
            )
            
            atencion_id = f"ATN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            nueva_fila = {
                "atencion_id": atencion_id,
                "profesional_id": data.get("profesional_id", ""),
                "profesional_nombre": data.get("profesional_nombre", ""),
                "paciente_id": data.get("pacienteId", ""),
                "paciente_nombre": data.get("paciente_nombre", ""),
                "paciente_rut": data.get("paciente_rut", ""),
                "paciente_edad": data.get("paciente_edad", ""),
                "fecha_hora": data.get("fecha_hora", ""),
                "tipo_atencion": data.get("tipo_atencion", ""),
                "motivo_consulta": data.get("motivo_consulta", ""),
                "diagnostico": data.get("diagnostico", ""),
                "tratamiento": data.get("tratamiento", ""),
                "observaciones": data.get("observaciones", ""),
                "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": data.get("estado", "completada"),
                "requiere_seguimiento": data.get("requiere_seguimiento", "No"),
                "tiene_archivos": data.get("tiene_archivos", "No"),
            }
            
            worksheet.append_row(list(nueva_fila.values()))
            logger.info(f"✅ Atención registrada en Sheets: {atencion_id}")
            
            # Si se proporcionaron datos del paciente, crear/actualizar registro en Pacientes_Profesional
            if (
                data.get("paciente_nombre")
                and data.get("paciente_rut")
                and data.get("profesional_id")
                and not data.get("pacienteId")
            ):
                
                logger.info("📝 Creando nuevo paciente en Pacientes_Profesional...")
                try:
                    # Crear registro del paciente
                    paciente_id = self._crear_paciente_desde_atencion(data, atencion_id)
                    
                    # Actualizar la atención con el paciente_id generado
                    nueva_fila["paciente_id"] = paciente_id
                    
                    # Actualizar la fila en la hoja (buscar por atencion_id y actualizar)
                    records = worksheet.get_all_records()
                    for i, record in enumerate(records):
                        if record.get("atencion_id") == atencion_id:
                            worksheet.update(
                                f"D{i+2}", [[paciente_id]]
                            )  # Columna D es paciente_id
                            break
                    
                    logger.info(
                        f"✅ Paciente {paciente_id} creado y vinculado a atención {atencion_id}"
                    )
                    
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
            headers_pacientes = [
                "paciente_id",
                "profesional_id",
                "nombre_completo",
                "rut",
                "edad",
                "fecha_nacimiento",
                "genero",
                "telefono",
                "email",
                "direccion",
                "antecedentes_medicos",
                "fecha_primera_consulta",
                "ultima_consulta",
                "num_atenciones",
                "estado_relacion",
                "fecha_registro",
                "notas",
            ]
            
            worksheet = self.get_or_create_worksheet(
                "Pacientes_Profesional", headers_pacientes
            )
            
            # Verificar si el paciente ya existe para este profesional
            records = worksheet.get_all_records()
            for i, record in enumerate(records):
                if (
                    str(record.get("profesional_id", ""))
                    == str(data.get("profesional_id", ""))
                    and record.get("rut", "").strip().lower()
                    == data.get("paciente_rut", "").strip().lower()
                ):
                    logger.info(
                        f"📋 Paciente con RUT {data.get('paciente_rut')} ya existe para profesional {data.get('profesional_id')}"
                    )
                    
                    # Actualizar contador de atenciones y última consulta
                    try:
                        num_atenciones = int(record.get("num_atenciones", 0)) + 1
                        worksheet.update(
                            f"N{i+2}", [[num_atenciones]]
                        )  # Columna N es num_atenciones
                        worksheet.update(
                            f"M{i+2}", [[data.get("fecha_hora", "")]]
                        )  # Columna M es ultima_consulta
                        logger.info(
                            f"✅ Actualizado contador de atenciones para paciente: {num_atenciones}"
                        )
                    except Exception as e:
                        logger.error(
                            f"❌ Error actualizando contador de atenciones: {e}"
                        )
                    
                    return record.get("paciente_id", "")
            
            # Generar ID único para el paciente
            paciente_id = f"PAC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Preparar datos del paciente
            nuevo_paciente = [
                paciente_id,
                data.get("profesional_id", ""),
                data.get("paciente_nombre", ""),
                data.get("paciente_rut", ""),
                data.get("paciente_edad", ""),
                data.get("paciente_fecha_nacimiento", ""),
                data.get("paciente_genero", ""),
                data.get("paciente_telefono", ""),
                data.get("paciente_email", ""),
                data.get("paciente_direccion", ""),
                data.get("paciente_antecedentes", ""),
                data.get("fecha_hora", ""),  # fecha_primera_consulta
                data.get("fecha_hora", ""),  # ultima_consulta
                1,  # num_atenciones (esta es la primera)
                "activo",  # estado_relacion
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                f"Paciente creado automáticamente desde atención {atencion_id}",
            ]
            
            # Insertar en Google Sheets
            worksheet.append_row(nuevo_paciente)
            logger.info(
                f"✅ Paciente {paciente_id} creado automáticamente desde atención"
            )
            
            return paciente_id
            
        except Exception as e:
            logger.error(f"Error creando paciente desde atención: {e}")
            raise

    def registrar_archivo_adjunto(self, data):
        """Registra un nuevo archivo adjunto en la hoja de cálculo."""
        try:
            worksheet = self.get_or_create_worksheet(
                "Archivos_Adjuntos", HEADERS_ARCHIVOS
            )
            
            archivo_id = f"FILE_{uuid.uuid4().hex[:12].upper()}"
            
            nueva_fila = [
                archivo_id,
                data.get("atencion_id"),
                data.get("nombre_archivo"),
                data.get("tipo_archivo"),
                data.get("ruta_archivo"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                data.get("tamaño"),
                "activo",  # estado
            ]
            
            worksheet.append_row(nueva_fila)
            logger.info(
                f"✅ Archivo adjunto registrado en Sheets: {archivo_id} para atención {data.get('atencion_id')}"
            )
            
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
            worksheet = self.spreadsheet.add_worksheet(
                title=title, rows=1000, cols=len(headers)
            )
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

    def batch_get_values(self, ranges: List[str], major_dimension: str = "ROWS"):
        """
        Obtiene múltiples rangos de valores en una sola llamada
        Usa spreadsheets.values.batchGet para optimizar
        """
        try:
            self._rate_limit()
            
            # Verificar que el spreadsheet esté disponible
            if not self.spreadsheet:
                logger.warning("⚠️ Spreadsheet no disponible, reconectando...")
                if not self.connect():
                    logger.error("❌ No se pudo reconectar al spreadsheet")
                    return None
            
            # Verificar que el objeto spreadsheet esté disponible
            if not self.spreadsheet:
                logger.error("❌ El objeto spreadsheet no está disponible")
                # Intentar reconectar
                if not self.connect():
                    return None
            
            # Crear clave de cache para batch
            cache_key = self._get_cache_key("batch_get", str(ranges), major_dimension)
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
            
            # Usar métodos de gspread para obtener múltiples rangos
            result = {"valueRanges": []}
            
            for range_str in ranges:
                try:
                    # Parsear el rango para obtener sheet_name y rango
                    if "!" in range_str:
                        sheet_name, cell_range = range_str.split("!", 1)
                        worksheet = self.spreadsheet.worksheet(sheet_name)
                        values = worksheet.get(cell_range)
                    else:
                        # Si no hay sheet especificado, usar la primera hoja
                        worksheet = self.spreadsheet.get_worksheet(0)
                        values = worksheet.get(range_str)
                    
                    result["valueRanges"].append(
                        {
                            "range": range_str,
                            "majorDimension": major_dimension,
                            "values": values,
                        }
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Error obteniendo rango {range_str}: {e}")
                    result["valueRanges"].append(
                        {
                            "range": range_str,
                            "majorDimension": major_dimension,
                            "values": [],
                        }
                    )
            
            # Guardar en cache
            self._set_cache(cache_key, result)
            
            logger.info(f"✅ Batch get ejecutado para {len(ranges)} rangos")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en batch_get_values: {e}")
            
            # Si es error 429, esperar y reintentar
            if "429" in str(e) or "quota" in str(e).lower():
                logger.warning(
                    "⚠️ Rate limit detectado en batch_get_values, esperando..."
                )
                time.sleep(10)  # Esperar 10 segundos
                
                # Reintentar una vez usando gspread
                try:
                    if self.spreadsheet:
                        result = {"valueRanges": []}
                        
                        for range_str in ranges:
                            try:
                                if "!" in range_str:
                                    sheet_name, cell_range = range_str.split("!", 1)
                                    worksheet = self.spreadsheet.worksheet(sheet_name)
                                    values = worksheet.get(cell_range)
                                else:
                                    worksheet = self.spreadsheet.get_worksheet(0)
                                    values = worksheet.get(range_str)
                                
                                result["valueRanges"].append(
                                    {
                                        "range": range_str,
                                        "majorDimension": major_dimension,
                                        "values": values,
                                    }
                                )
                            except Exception as range_error:
                                logger.warning(
                                    f"⚠️ Error en reintento rango {range_str}: {range_error}"
                                )
                                result["valueRanges"].append(
                                    {
                                        "range": range_str,
                                        "majorDimension": major_dimension,
                                        "values": [],
                                    }
                                )
                        
                        logger.info("✅ Batch get exitoso después de reintento")
                        return result
                except Exception as retry_error:
                    logger.error(
                        f"❌ Error en reintento de batch_get_values: {retry_error}"
                    )
            
            return None
    
    def batch_update_values(self, updates: List[Dict]):
        """
        Actualiza múltiples rangos en una sola llamada
        Usa spreadsheets.values.batchUpdate para optimizar
        """
        try:
            self._rate_limit()
            
            # Preparar datos para batchUpdate
            data = []
            for update in updates:
                data.append({"range": update["range"], "values": update["values"]})
            
            # Ejecutar actualizaciones usando gspread
            result = {
                "updatedCells": 0,
                "updatedRows": 0,
                "updatedColumns": 0,
                "updatedRanges": [],
            }
            
            for update in updates:
                try:
                    range_str = update["range"]
                    values = update["values"]
                    
                    # Parsear el rango para obtener sheet_name y rango
                    if "!" in range_str:
                        sheet_name, cell_range = range_str.split("!", 1)
                        worksheet = self.spreadsheet.worksheet(sheet_name)
                    else:
                        # Si no hay sheet especificado, usar la primera hoja
                        worksheet = self.spreadsheet.get_worksheet(0)
                        cell_range = range_str
                    
                    # Actualizar usando gspread
                    worksheet.update(
                        cell_range, values, value_input_option="USER_ENTERED"
                    )
                    
                    result["updatedRanges"].append(range_str)
                    result["updatedCells"] += (
                        len(values) * len(values[0]) if values and values[0] else 0
                    )
                    result["updatedRows"] += len(values) if values else 0
                    
                except Exception as e:
                    logger.error(
                        f"❌ Error actualizando rango {update.get('range', 'unknown')}: {e}"
                    )
            
            logger.info(f"✅ Batch update ejecutado para {len(updates)} rangos")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en batch_update_values: {e}")
            return None
    
    def get_worksheet_with_fields(self, sheet_name: str, fields: List[str] = None):
        """
        Obtiene una hoja con campos específicos usando field masks
        Reduce la cantidad de datos transferidos
        """
        try:
            self._rate_limit()
            
            # Crear clave de cache con campos
            cache_key = self._get_cache_key("worksheet_fields", sheet_name, str(fields))
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
            
            # Obtener worksheet con field mask si se especifica
            if fields:
                # Usar field mask para obtener solo campos específicos
                worksheet = self.spreadsheet.worksheet(sheet_name)
                # Nota: gspread no soporta field masks directamente
                # Esta es una implementación básica
                all_values = worksheet.get_all_values()
                
                # Filtrar por campos si es necesario
                if all_values and fields:
                    headers = all_values[0]
                    field_indices = [
                        headers.index(field) for field in fields if field in headers
                    ]
                    filtered_values = []
                    for row in all_values:
                        filtered_row = [row[i] for i in field_indices if i < len(row)]
                        filtered_values.append(filtered_row)
                    
                    result = {"values": filtered_values, "fields": fields}
                else:
                    result = {"values": all_values, "fields": fields}
            else:
                # Obtener worksheet completo
                worksheet = self.spreadsheet.worksheet(sheet_name)
                result = {"values": worksheet.get_all_values(), "fields": None}
            
            # Guardar en cache
            self._set_cache(cache_key, result)
            
            logger.info(f"✅ Worksheet obtenido con fields: {fields}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo worksheet con fields: {e}")
            return None
    
    def optimized_get_all_records(self, sheet_name: str, fields: List[str] = None):
        """
        Versión optimizada de get_all_records con field masks
        """
        try:
            result = self.get_worksheet_with_fields(sheet_name, fields)
            if not result or "values" not in result:
                return []
            
            values = result["values"]
            if not values:
                return []
            
            # Convertir a records
            headers = values[0]
            records = []
            
            for row in values[1:]:
                record = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        record[header] = row[i]
                    else:
                        record[header] = ""
                records.append(record)
            
            logger.info(f"✅ Records optimizados obtenidos: {len(records)} registros")
            return records
            
        except Exception as e:
            logger.error(f"❌ Error en optimized_get_all_records: {e}")
            return []

    def optimized_get_user_data(self, user_id: str):
        """
        Obtiene todos los datos de un usuario en una sola operación batch
        """
        try:
            # Definir rangos para obtener todos los datos del usuario
            ranges = [
                f"Usuarios!A:L",  # Datos básicos del usuario
                f"Atenciones_Medicas!A:N",  # Atenciones médicas
                f"Medicamentos!A:K",  # Medicamentos
                f"Examenes!A:I",  # Exámenes
                f"Familiares!A:H",  # Familiares autorizados
            ]
            
            # Obtener todos los datos en batch
            batch_result = self.batch_get_values(ranges)
            if not batch_result or "valueRanges" not in batch_result:
                return None
            
            # Procesar resultados
            user_data = {
                "user_info": None,
                "atenciones": [],
                "medicamentos": [],
                "examenes": [],
                "familiares": [],
            }
            
            # Procesar cada rango
            for i, value_range in enumerate(batch_result["valueRanges"]):
                values = value_range.get("values", [])
                if not values:
                    continue
                
                headers = values[0]
                records = []
                
                for row in values[1:]:
                    record = {}
                    for j, header in enumerate(headers):
                        if j < len(row):
                            record[header] = row[j]
                        else:
                            record[header] = ""
                    records.append(record)
                
                # Asignar a la estructura correspondiente
                if i == 0:  # Usuarios
                    user_data["user_info"] = next(
                        (r for r in records if r.get("user_id") == user_id), None
                    )
                elif i == 1:  # Atenciones
                    user_data["atenciones"] = [
                        r for r in records if r.get("user_id") == user_id
                    ]
                elif i == 2:  # Medicamentos
                    user_data["medicamentos"] = [
                        r for r in records if r.get("user_id") == user_id
                    ]
                elif i == 3:  # Exámenes
                    user_data["examenes"] = [
                        r for r in records if r.get("user_id") == user_id
                    ]
                elif i == 4:  # Familiares
                    user_data["familiares"] = [
                        r for r in records if r.get("user_id") == user_id
                    ]
            
            logger.info(f"✅ Datos de usuario obtenidos en batch: {user_id}")
            return user_data
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos de usuario en batch: {e}")
            return None
    
    def optimized_create_multiple_records(self, sheet_name: str, records: List[Dict]):
        """
        Crea múltiples registros en una sola operación batch
        """
        try:
            if not records:
                return []
            
            # Obtener headers de la hoja
            worksheet = self.get_worksheet(sheet_name)
            if not worksheet:
                return []
            
            # Preparar datos para batch update
            values = []
            for record in records:
                row = []
                for key, value in record.items():
                    row.append(str(value) if value is not None else "")
                values.append(row)
            
            # Ejecutar batch update
            update_data = [
                {"range": f"{sheet_name}!A:Z", "values": values}  # Rango dinámico
            ]
            
            result = self.batch_update_values(update_data)
            
            if result:
                logger.info(
                    f"✅ {len(records)} registros creados en batch en {sheet_name}"
                )
                return [f"Record_{i}" for i in range(len(records))]
            else:
                logger.error(f"❌ Error creando registros en batch en {sheet_name}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error en optimized_create_multiple_records: {e}")
            return []
    
    def optimized_update_multiple_records(self, sheet_name: str, updates: List[Dict]):
        """
        Actualiza múltiples registros en una sola operación batch
        """
        try:
            if not updates:
                return False
            
            # Preparar datos para batch update
            batch_updates = []
            
            for update in updates:
                record_id = update.get("id")
                if not record_id:
                    continue
                
                # Encontrar la fila del registro
                worksheet = self.get_worksheet(sheet_name)
                if not worksheet:
                    continue
                
                all_values = worksheet.get_all_values()
                headers = all_values[0] if all_values else []
                
                # Buscar la fila del registro
                row_index = None
                for i, row in enumerate(all_values[1:], start=2):
                    if row and len(row) > 0 and str(row[0]) == str(record_id):
                        row_index = i
                        break
                
                if row_index:
                    # Preparar actualización
                    for field, value in update.items():
                        if field != "id" and field in headers:
                            col_index = headers.index(field) + 1
                            batch_updates.append(
                                {
                                    "range": f"{sheet_name}!{chr(64 + col_index)}{row_index}",
                                    "values": [[str(value)]],
                                }
                            )
            
            # Ejecutar batch update
            if batch_updates:
                result = self.batch_update_values(batch_updates)
                if result:
                    logger.info(
                        f"✅ {len(updates)} registros actualizados en batch en {sheet_name}"
                    )
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error en optimized_update_multiple_records: {e}")
            return False
    
    def get_professional_schedule_optimized(
        self, professional_id: str, fecha_inicio: str = None, fecha_fin: str = None
    ):
        """
        Obtiene la agenda del profesional de manera optimizada usando batch operations
        """
        try:
            # Rate limiting
            self._rate_limit()
            
            # Crear clave de cache
            cache_key = self._get_cache_key(
                "schedule", professional_id, fecha_inicio, fecha_fin
            )
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
            
            # Verificar que el spreadsheet esté disponible
            if not self.spreadsheet:
                logger.warning(
                    "⚠️ Spreadsheet no disponible en get_professional_schedule_optimized"
                )
                return []
            
            # Obtener datos en batch
            ranges = [
                "Citas!A:Z",  # Todas las citas
                "Profesionales!A:L",  # Información de profesionales
            ]
            
            batch_result = self.batch_get_values(ranges)
            if not batch_result or "valueRanges" not in batch_result:
                logger.warning(
                    "⚠️ No se pudieron obtener datos en batch, usando método individual"
                )
                return self.get_professional_schedule_fallback(
                    professional_id, fecha_inicio, fecha_fin
                )
            
            # Procesar resultados
            citas = []
            profesionales = {}
            
            # Procesar citas
            if len(batch_result["valueRanges"]) > 0:
                citas_values = batch_result["valueRanges"][0].get("values", [])
                if citas_values:
                    headers = citas_values[0]
                    for row in citas_values[1:]:
                        if len(row) >= len(headers):
                            cita = {}
                            for i, header in enumerate(headers):
                                if i < len(row):
                                    cita[header] = row[i]
                                else:
                                    cita[header] = ""
                            
                            # Filtrar por profesional y fechas
                            if cita.get("profesional_id") == professional_id:
                                if fecha_inicio and fecha_fin:
                                    fecha_cita = cita.get("fecha", "")
                                    if fecha_inicio <= fecha_cita <= fecha_fin:
                                        citas.append(cita)
                                else:
                                    citas.append(cita)
            
            # Procesar profesionales
            if len(batch_result["valueRanges"]) > 1:
                prof_values = batch_result["valueRanges"][1].get("values", [])
                if prof_values:
                    headers = prof_values[0]
                    for row in prof_values[1:]:
                        if len(row) >= len(headers):
                            prof = {}
                            for i, header in enumerate(headers):
                                if i < len(row):
                                    prof[header] = row[i]
                                else:
                                    prof[header] = ""
                            profesionales[prof.get("id", "")] = prof
            
            # Guardar en cache
            result = {
                "citas": citas,
                "profesional": profesionales.get(professional_id, {}),
            }
            self._set_cache(cache_key, result)
            
            logger.info(
                f"✅ Agenda optimizada obtenida para profesional {professional_id}: {len(citas)} citas"
            )
            return result
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo agenda optimizada: {e}")
            return self.get_professional_schedule_fallback(
                professional_id, fecha_inicio, fecha_fin
            )
    
    def get_professional_schedule_fallback(
        self, professional_id: str, fecha_inicio: str = None, fecha_fin: str = None
    ):
        """
        Método de fallback para obtener agenda usando métodos individuales
        """
        try:
            logger.info(
                f"🔄 Usando método de fallback para agenda del profesional {professional_id}"
            )
            
            citas = []
            profesional = {}
            
            # Obtener citas individualmente
            try:
                worksheet = self.get_worksheet("Citas")
                if worksheet:
                    all_citas = worksheet.get_all_records()
                    for cita in all_citas:
                        if cita.get("profesional_id") == professional_id:
                            if fecha_inicio and fecha_fin:
                                fecha_cita = cita.get("fecha", "")
                                if fecha_inicio <= fecha_cita <= fecha_fin:
                                    citas.append(cita)
                            else:
                                citas.append(cita)
            except Exception as e:
                logger.error(f"❌ Error obteniendo citas en fallback: {e}")
            
            # Obtener información del profesional
            try:
                prof_worksheet = self.get_worksheet("Profesionales")
                if prof_worksheet:
                    all_profesionales = prof_worksheet.get_all_records()
                    profesional = next(
                        (
                            p
                            for p in all_profesionales
                            if p.get("id") == professional_id
                        ),
                        {},
                    )
            except Exception as e:
                logger.error(f"❌ Error obteniendo profesional en fallback: {e}")
            
            result = {"citas": citas, "profesional": profesional}
            
            logger.info(f"✅ Fallback exitoso: {len(citas)} citas encontradas")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en método de fallback: {e}")
            return {"citas": [], "profesional": {}}
    
    def get_user_active_reminders(self, user_id: str):
        """
        Obtiene los recordatorios activos de un usuario de manera optimizada
        """
        try:
            self._rate_limit()
            
            # Crear clave de cache
            cache_key = self._get_cache_key("reminders", user_id)
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
            
            # Verificar que el spreadsheet esté disponible
            if not self.spreadsheet:
                logger.warning(
                    "⚠️ Spreadsheet no disponible en get_user_active_reminders"
                )
                return None
            
            # Obtener recordatorios usando batch
            ranges = ["Recordatorios_Profesional!A:M"]
            batch_result = self.batch_get_values(ranges)
            
            if not batch_result or "valueRanges" not in batch_result:
                logger.warning("⚠️ No se pudieron obtener recordatorios en batch")
                return self.get_user_active_reminders_fallback(user_id)
            
            # Procesar resultados
            recordatorios = []
            if len(batch_result["valueRanges"]) > 0:
                values = batch_result["valueRanges"][0].get("values", [])
                if values:
                    headers = values[0]
                    for row in values[1:]:
                        if len(row) >= len(headers):
                            recordatorio = {}
                            for i, header in enumerate(headers):
                                if i < len(row):
                                    recordatorio[header] = row[i]
                                else:
                                    recordatorio[header] = ""
                            
                            # Filtrar por usuario y estado activo
                            if (
                                str(recordatorio.get("profesional_id", ""))
                                == str(user_id)
                                and recordatorio.get("estado", "") == "activo"
                            ):
                                recordatorios.append(
                                    {
                                        "id": recordatorio.get("recordatorio_id", ""),
                                        "tipo": recordatorio.get("tipo", ""),
                                        "paciente_id": recordatorio.get(
                                            "paciente_id", ""
                                        ),
                                        "titulo": recordatorio.get("titulo", ""),
                                        "mensaje": recordatorio.get("mensaje", ""),
                                        "fecha": recordatorio.get("fecha", ""),
                                        "hora": recordatorio.get("hora", ""),
                                        "prioridad": recordatorio.get(
                                            "prioridad", "media"
                                        ),
                                        "repetir": recordatorio.get(
                                            "repetir", "false"
                                        ).lower()
                                        == "true",
                                        "tipo_repeticion": recordatorio.get(
                                            "tipo_repeticion", ""
                                        ),
                                        "estado": recordatorio.get("estado", "activo"),
                                    }
                                )
            
            # Guardar en cache
            self._set_cache(cache_key, recordatorios)
            
            logger.info(
                f"✅ Recordatorios obtenidos para usuario {user_id}: {len(recordatorios)} recordatorios"
            )
            return recordatorios
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo recordatorios optimizados: {e}")
            return self.get_user_active_reminders_fallback(user_id)
    
    def get_user_active_reminders_fallback(self, user_id: str):
        """
        Método de fallback para obtener recordatorios usando métodos individuales
        """
        try:
            logger.info(
                f"🔄 Usando método de fallback para recordatorios del usuario {user_id}"
            )
            
            recordatorios = []
            
            try:
                worksheet = self.get_worksheet("Recordatorios_Profesional")
                if worksheet:
                    all_records = worksheet.get_all_records()
                    for record in all_records:
                        if (
                            str(record.get("profesional_id", "")) == str(user_id)
                            and record.get("estado", "") == "activo"
                        ):
                            recordatorios.append(
                                {
                                    "id": record.get("recordatorio_id", ""),
                                    "tipo": record.get("tipo", ""),
                                    "paciente_id": record.get("paciente_id", ""),
                                    "titulo": record.get("titulo", ""),
                                    "mensaje": record.get("mensaje", ""),
                                    "fecha": record.get("fecha", ""),
                                    "hora": record.get("hora", ""),
                                    "prioridad": record.get("prioridad", "media"),
                                    "repetir": record.get("repetir", "false").lower()
                                    == "true",
                                    "tipo_repeticion": record.get(
                                        "tipo_repeticion", ""
                                    ),
                                    "estado": record.get("estado", "activo"),
                                }
                            )
            except Exception as e:
                logger.error(f"❌ Error obteniendo recordatorios en fallback: {e}")
            
            logger.info(
                f"✅ Fallback exitoso: {len(recordatorios)} recordatorios encontrados"
            )
            return recordatorios
            
        except Exception as e:
            logger.error(f"❌ Error en método de fallback de recordatorios: {e}")
            return []

    def get_data_with_fallback(self, method_name: str, *args, **kwargs):
        """
        Método genérico que intenta obtener datos con fallback
        """
        try:
            # Intentar método optimizado
            if hasattr(self, f"{method_name}_optimized"):
                result = getattr(self, f"{method_name}_optimized")(*args, **kwargs)
                if result is not None:
                    logger.info(f"✅ {method_name} exitoso con método optimizado")
                    return result
            
            # Si falla, usar método de fallback
            if hasattr(self, f"{method_name}_fallback"):
                logger.warning(
                    f"⚠️ Método optimizado falló, usando fallback: {method_name}"
                )
                result = getattr(self, f"{method_name}_fallback")(*args, **kwargs)
                if result is not None:
                    logger.info(f"✅ {method_name} exitoso con fallback")
                    return result
            
            # Si ambos fallan, retornar datos vacíos
            logger.error(f"❌ Ambos métodos fallaron para: {method_name}")
            return []
            
        except Exception as e:
            logger.error(f"❌ Error en get_data_with_fallback: {e}")
            return []

    def is_connected(self):
        """Verificar si está conectado a Google Sheets"""
        return (
            not self.use_fallback
            and self.gc is not None
            and self.spreadsheet is not None
        )

    def get_fallback_data(self, sheet_name: str):
        """Obtener datos de fallback para diferentes hojas"""
        logger.info(f"🔧 Usando datos de fallback para: {sheet_name}")

        if sheet_name.lower() == "atenciones":
            return self._get_fallback_atenciones()
        elif sheet_name.lower() == "pacientes":
            return self._get_fallback_pacientes()
        elif sheet_name.lower() == "agenda":
            return self._get_fallback_agenda()
        elif sheet_name.lower() == "usuarios":
            return self._get_fallback_usuarios()
        else:
            return []

    def _get_fallback_atenciones(self):
        """Datos de fallback para atenciones"""
        return [
            {
                "id": 1,
                "paciente_id": 2,
                "profesional_id": 1,
                "fecha": "2025-08-30",
                "hora": "10:00",
                "motivo": "Consulta de rutina",
                "diagnostico": "Paciente sano",
                "tratamiento": "Continuar con hábitos saludables",
                "estado": "completada",
                "notas": "Paciente presenta buen estado general",
            },
            {
                "id": 2,
                "paciente_id": 2,
                "profesional_id": 1,
                "fecha": "2025-08-31",
                "hora": "14:30",
                "motivo": "Seguimiento",
                "diagnostico": "En observación",
                "tratamiento": "Continuar tratamiento actual",
                "estado": "programada",
                "notas": "Cita de seguimiento programada",
            },
        ]

    def _get_fallback_pacientes(self):
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
                "tipo_usuario": "paciente",
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
                "tipo_usuario": "paciente",
            },
        ]

    def _get_fallback_agenda(self):
        """Datos de fallback para agenda"""
        return [
            {
                "id": 1,
                "profesional_id": 1,
                "fecha": "2025-08-30",
                "hora_inicio": "09:00",
                "hora_fin": "17:00",
                "disponible": True,
                "notas": "Horario normal de atención",
            },
            {
                "id": 2,
                "profesional_id": 1,
                "fecha": "2025-08-31",
                "hora_inicio": "09:00",
                "hora_fin": "17:00",
                "disponible": True,
                "notas": "Horario normal de atención",
            },
        ]

    def _get_fallback_usuarios(self):
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
            },
        ]

    def get_all_records_fallback(self, sheet_name: str):
        """Obtener todos los registros con fallback"""
        if self.use_fallback:
            return self.get_fallback_data(sheet_name)

        try:
            worksheet = self.get_worksheet(sheet_name)
            if worksheet:
                return worksheet.get_all_records()
            else:
                return self.get_fallback_data(sheet_name)
        except Exception as e:
            logger.error(f"❌ Error obteniendo registros de {sheet_name}: {e}")
            return self.get_fallback_data(sheet_name)


# Instancia global del gestor
sheets_db = SheetsManager() 
