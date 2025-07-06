#!/usr/bin/env python3
"""
Script de inicialización robusto para SheetsManager
Maneja errores de rate limiting y proporciona fallbacks
"""

import time
import logging
from backend.database.sheets_manager import SheetsManager

logger = logging.getLogger(__name__)

def initialize_sheets_manager_with_retry(max_attempts=5, base_delay=2):
    """
    Inicializa SheetsManager con reintentos automáticos
    """
    logger.info("🔄 Inicializando SheetsManager con reintentos...")
    
    for attempt in range(max_attempts):
        try:
            logger.info(f"📋 Intento {attempt + 1}/{max_attempts}")
            
            # Crear instancia
            sheets_manager = SheetsManager()
            
            # Verificar conexión
            if sheets_manager.spreadsheet:
                logger.info("✅ SheetsManager inicializado exitosamente")
                return sheets_manager
            else:
                logger.warning(f"⚠️ Intento {attempt + 1} falló, reintentando...")
                
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"⚠️ Error en intento {attempt + 1}: {error_msg}")
            
            # Si es error de rate limiting, esperar más tiempo
            if "429" in error_msg or "quota" in error_msg.lower():
                wait_time = base_delay * (2 ** attempt)  # Exponential backoff
                logger.info(f"⏳ Rate limit detectado, esperando {wait_time} segundos...")
                time.sleep(wait_time)
            else:
                # Para otros errores, esperar menos tiempo
                wait_time = base_delay
                logger.info(f"⏳ Error de conexión, esperando {wait_time} segundos...")
                time.sleep(wait_time)
    
    # Si todos los intentos fallaron
    logger.error("❌ No se pudo inicializar SheetsManager después de múltiples intentos")
    return None

def create_fallback_sheets_manager():
    """
    Crea un SheetsManager con configuración de fallback
    """
    logger.info("🔄 Creando SheetsManager con configuración de fallback...")
    
    try:
        # Configurar límites más conservadores
        sheets_manager = SheetsManager()
        sheets_manager.max_requests_per_minute = 30  # Más conservador
        sheets_manager.cache_duration = 60  # Cache más largo
        
        logger.info("✅ SheetsManager de fallback creado")
        return sheets_manager
        
    except Exception as e:
        logger.error(f"❌ Error creando SheetsManager de fallback: {e}")
        return None

# Función principal para obtener SheetsManager
def get_sheets_manager():
    """
    Obtiene una instancia de SheetsManager con manejo robusto de errores
    """
    # Intentar inicialización normal
    sheets_manager = initialize_sheets_manager_with_retry()
    
    if sheets_manager:
        return sheets_manager
    
    # Si falla, usar configuración de fallback
    logger.warning("⚠️ Usando configuración de fallback para SheetsManager")
    return create_fallback_sheets_manager()

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Probar inicialización
    manager = get_sheets_manager()
    
    if manager:
        print("✅ SheetsManager inicializado correctamente")
        print(f"📊 Configuración: {manager.max_requests_per_minute} req/min, {manager.cache_duration}s cache")
    else:
        print("❌ No se pudo inicializar SheetsManager") 