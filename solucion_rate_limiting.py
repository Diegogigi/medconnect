#!/usr/bin/env python3
"""
Solución para errores de rate limiting y problemas de conexión con Google Sheets
"""

import time
import logging
import json
import os
from typing import Dict, List, Optional, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_sheets_manager():
    """Corrige los problemas en SheetsManager"""
    
    print("🔧 Solucionando problemas en SheetsManager...")
    
    # 1. Mejorar rate limiting
    rate_limiting_fix = '''
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
                logger.warning(f"⚠️ Rate limit alcanzado, esperando {wait_time:.2f} segundos")
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
    '''
    
    # 2. Mejorar método batch_get_values
    batch_get_fix = '''
    def batch_get_values(self, ranges: List[str], major_dimension: str = 'ROWS'):
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
            
            # Verificar que el objeto spreadsheet tenga el método values
            if not hasattr(self.spreadsheet, 'values'):
                logger.error("❌ El objeto spreadsheet no tiene el método 'values'")
                # Intentar reconectar
                if not self.connect():
                    return None
            
            # Crear clave de cache para batch
            cache_key = self._get_cache_key("batch_get", str(ranges), major_dimension)
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
            
            # Usar batchGet para múltiples rangos
            result = self.spreadsheet.values().batchGet(
                ranges=ranges,
                majorDimension=major_dimension
            ).execute()
            
            # Guardar en cache
            self._set_cache(cache_key, result)
            
            logger.info(f"✅ Batch get ejecutado para {len(ranges)} rangos")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en batch_get_values: {e}")
            
            # Si es error 429, esperar y reintentar
            if "429" in str(e) or "quota" in str(e).lower():
                logger.warning("⚠️ Rate limit detectado en batch_get_values, esperando...")
                time.sleep(10)  # Esperar 10 segundos
                
                # Reintentar una vez
                try:
                    if self.spreadsheet and hasattr(self.spreadsheet, 'values'):
                        result = self.spreadsheet.values().batchGet(
                            ranges=ranges,
                            majorDimension=major_dimension
                        ).execute()
                        logger.info("✅ Batch get exitoso después de reintento")
                        return result
                except Exception as retry_error:
                    logger.error(f"❌ Error en reintento de batch_get_values: {retry_error}")
            
            return None
    '''
    
    # 3. Mejorar método connect
    connect_fix = '''
    def connect(self):
        """Conecta con Google Sheets con manejo de errores mejorado"""
        try:
            # Rate limiting antes de conectar
            self._rate_limit()
            
            # Configurar credenciales
            if os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'):
                service_account_info = json.loads(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'))
                # Agregar scopes específicos para Google Sheets
                scopes = [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
                creds = Credentials.from_service_account_info(
                    service_account_info,
                    scopes=scopes
                )
                logger.info("✅ Credenciales cargadas desde GOOGLE_SERVICE_ACCOUNT_JSON")
            else:
                logger.error("❌ GOOGLE_SERVICE_ACCOUNT_JSON no configurado")
                return False
            
            # Crear cliente con retry automático
            self.gc = gspread.authorize(creds)
            
            # Intentar conectar con retry
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    self.spreadsheet = self.gc.open_by_key(Config.GOOGLE_SHEETS_ID)
                    
                    # Verificar que el objeto tenga los métodos necesarios
                    if not hasattr(self.spreadsheet, 'values'):
                        logger.error("❌ El objeto spreadsheet no tiene el método 'values'")
                        return False
                    
                    logger.info("✅ Conexión exitosa con Google Sheets")
                    return True
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"⚠️ Rate limit detectado, esperando {wait_time} segundos (intento {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"❌ Error conectando con Google Sheets: {e}")
                        return False
            
            logger.error("❌ No se pudo conectar después de múltiples intentos")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error en connect(): {e}")
            return False
    '''
    
    print("✅ Código de corrección generado")
    print("\n📋 Para aplicar las correcciones:")
    print("1. Abre el archivo backend/database/sheets_manager.py")
    print("2. Reemplaza los métodos correspondientes con el código de arriba")
    print("3. Reinicia la aplicación")
    
    return {
        'rate_limiting_fix': rate_limiting_fix,
        'batch_get_fix': batch_get_fix,
        'connect_fix': connect_fix
    }

def create_fallback_system():
    """Crea un sistema de fallback para cuando la API falla"""
    
    fallback_code = '''
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
                logger.warning(f"⚠️ Método optimizado falló, usando fallback: {method_name}")
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
    '''
    
    print("✅ Sistema de fallback generado")
    return fallback_code

def main():
    """Función principal"""
    print("🚀 Iniciando solución para errores de Google Sheets API...")
    
    # Generar correcciones
    fixes = fix_sheets_manager()
    fallback = create_fallback_system()
    
    print("\n📝 Resumen de problemas identificados:")
    print("1. Rate limiting insuficiente (error 429)")
    print("2. Objeto spreadsheet sin método 'values'")
    print("3. Falta de verificación de métodos del objeto")
    print("4. Sistema de fallback incompleto")
    
    print("\n🔧 Soluciones propuestas:")
    print("1. Mejorar rate limiting con límites más conservadores")
    print("2. Agregar verificación de métodos del objeto spreadsheet")
    print("3. Implementar sistema de fallback robusto")
    print("4. Aumentar tiempos de espera para reintentos")
    
    print("\n✅ Correcciones generadas exitosamente")

if __name__ == "__main__":
    main() 