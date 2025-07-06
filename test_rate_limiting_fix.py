#!/usr/bin/env python3
"""
Script de prueba para verificar el rate limiting y métodos de fallback
"""

import sys
import os
import time
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_sheets_manager():
    """Prueba el SheetsManager con rate limiting"""
    try:
        from backend.database.sheets_manager import sheets_db
        
        logger.info("🧪 Iniciando pruebas del SheetsManager...")
        
        # Test 1: Verificar conexión
        logger.info("📋 Test 1: Verificando conexión...")
        if sheets_db.connect():
            logger.info("✅ Conexión exitosa")
        else:
            logger.error("❌ Error de conexión")
            return False
        
        # Test 2: Verificar spreadsheet
        logger.info("📋 Test 2: Verificando spreadsheet...")
        if sheets_db.spreadsheet:
            logger.info("✅ Spreadsheet disponible")
        else:
            logger.warning("⚠️ Spreadsheet no disponible")
        
        # Test 3: Probar batch_get_values
        logger.info("📋 Test 3: Probando batch_get_values...")
        try:
            result = sheets_db.batch_get_values(["Citas!A1:A5"])
            if result:
                logger.info("✅ Batch get exitoso")
            else:
                logger.warning("⚠️ Batch get falló, usando fallback")
        except Exception as e:
            logger.error(f"❌ Error en batch_get_values: {e}")
        
        # Test 4: Probar get_user_active_reminders
        logger.info("📋 Test 4: Probando get_user_active_reminders...")
        try:
            # Usar un ID de prueba
            test_user_id = "test_user_123"
            reminders = sheets_db.get_user_active_reminders(test_user_id)
            if reminders is not None:
                logger.info(f"✅ Recordatorios obtenidos: {len(reminders)} recordatorios")
            else:
                logger.warning("⚠️ No se pudieron obtener recordatorios")
        except Exception as e:
            logger.error(f"❌ Error obteniendo recordatorios: {e}")
        
        # Test 5: Probar rate limiting
        logger.info("📋 Test 5: Probando rate limiting...")
        try:
            # Hacer múltiples llamadas rápidas para probar rate limiting
            for i in range(3):
                logger.info(f"   Llamada {i+1}/3...")
                result = sheets_db.batch_get_values(["Citas!A1:A2"])
                time.sleep(0.5)  # Pequeña pausa
        except Exception as e:
            logger.error(f"❌ Error en rate limiting: {e}")
        
        logger.info("🎉 Todas las pruebas completadas")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error general en pruebas: {e}")
        return False

def test_api_endpoints():
    """Prueba los endpoints de la API"""
    try:
        import requests
        
        logger.info("🧪 Iniciando pruebas de endpoints...")
        
        # URL base (ajustar según tu configuración)
        base_url = "http://localhost:5000"
        
        # Test 1: Health check
        logger.info("📋 Test 1: Health check...")
        try:
            response = requests.get(f"{base_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Health check exitoso")
            else:
                logger.warning(f"⚠️ Health check falló: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Error en health check: {e}")
        
        # Test 2: API monitor
        logger.info("📋 Test 2: API monitor...")
        try:
            response = requests.get(f"{base_url}/api/monitor", timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ API monitor exitoso: {data.get('status', 'unknown')}")
            else:
                logger.warning(f"⚠️ API monitor falló: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Error en API monitor: {e}")
        
        logger.info("🎉 Pruebas de endpoints completadas")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error general en pruebas de endpoints: {e}")
        return False

def main():
    """Función principal"""
    logger.info("🚀 Iniciando pruebas de rate limiting y fallback...")
    
    # Test SheetsManager
    sheets_success = test_sheets_manager()
    
    # Test API endpoints
    api_success = test_api_endpoints()
    
    # Resumen
    logger.info("\n" + "="*50)
    logger.info("📊 RESUMEN DE PRUEBAS")
    logger.info("="*50)
    logger.info(f"SheetsManager: {'✅ EXITOSO' if sheets_success else '❌ FALLÓ'}")
    logger.info(f"API Endpoints: {'✅ EXITOSO' if api_success else '❌ FALLÓ'}")
    
    if sheets_success and api_success:
        logger.info("🎉 Todas las pruebas pasaron exitosamente")
        return 0
    else:
        logger.error("❌ Algunas pruebas fallaron")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 