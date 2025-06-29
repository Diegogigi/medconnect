#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la conectividad del bot de Telegram
y las configuraciones de MedConnect
"""

import os
import json
import requests
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_environment_variables():
    """Verifica las variables de entorno críticas"""
    logger.info("🔍 === VERIFICANDO VARIABLES DE ENTORNO ===")
    
    required_vars = {
        'TELEGRAM_BOT_TOKEN': os.environ.get('TELEGRAM_BOT_TOKEN'),
        'GOOGLE_SHEETS_ID': os.environ.get('GOOGLE_SHEETS_ID'),
        'GOOGLE_SERVICE_ACCOUNT_JSON': os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'),
    }
    
    all_ok = True
    for var_name, var_value in required_vars.items():
        if var_value:
            if var_name == 'GOOGLE_SERVICE_ACCOUNT_JSON':
                logger.info(f"✅ {var_name}: Configurado ({len(var_value)} caracteres)")
                # Verificar que sea JSON válido
                try:
                    json_data = json.loads(var_value)
                    logger.info(f"   📝 Proyecto: {json_data.get('project_id', 'N/A')}")
                    logger.info(f"   📝 Tipo: {json_data.get('type', 'N/A')}")
                except json.JSONDecodeError as e:
                    logger.error(f"   ❌ JSON inválido: {e}")
                    all_ok = False
            else:
                logger.info(f"✅ {var_name}: Configurado")
        else:
            logger.error(f"❌ {var_name}: NO configurado")
            all_ok = False
    
    return all_ok

def test_telegram_bot():
    """Verifica la conectividad del bot de Telegram"""
    logger.info("\n🤖 === VERIFICANDO BOT DE TELEGRAM ===")
    
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("❌ Token del bot no disponible")
        return False
    
    try:
        # Test getMe
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info['ok']:
                logger.info(f"✅ Bot conectado exitosamente")
                logger.info(f"   📝 Nombre: {bot_info['result']['first_name']}")
                logger.info(f"   📝 Username: @{bot_info['result']['username']}")
                logger.info(f"   📝 ID: {bot_info['result']['id']}")
                return True
            else:
                logger.error(f"❌ Error del bot: {bot_info.get('description', 'Unknown')}")
                return False
        else:
            logger.error(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error de conexión: {e}")
        return False

def test_google_sheets():
    """Verifica la conexión a Google Sheets"""
    logger.info("\n📊 === VERIFICANDO GOOGLE SHEETS ===")
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Obtener credenciales
        json_content = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        sheets_id = os.environ.get('GOOGLE_SHEETS_ID')
        
        if not json_content or not sheets_id:
            logger.error("❌ Credenciales o ID de sheet no disponibles")
            return False
        
        # Crear credenciales
        service_account_info = json.loads(json_content)
        credentials = Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        # Conectar a Google Sheets
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open_by_key(sheets_id)
        
        logger.info(f"✅ Google Sheets conectado exitosamente")
        logger.info(f"   📝 Título: {spreadsheet.title}")
        logger.info(f"   📝 URL: {spreadsheet.url}")
        
        # Listar worksheets
        worksheets = spreadsheet.worksheets()
        logger.info(f"   📋 Hojas disponibles: {[ws.title for ws in worksheets]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error conectando a Google Sheets: {e}")
        return False

def test_webhook_url():
    """Verifica la URL del webhook"""
    logger.info("\n🌐 === VERIFICANDO WEBHOOK ===")
    
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("❌ Token no disponible para webhook")
        return False
    
    try:
        # Obtener información del webhook actual
        response = requests.get(f"https://api.telegram.org/bot{token}/getWebhookInfo", timeout=10)
        if response.status_code == 200:
            webhook_info = response.json()
            if webhook_info['ok']:
                result = webhook_info['result']
                if result.get('url'):
                    logger.info(f"✅ Webhook configurado: {result['url']}")
                    logger.info(f"   📝 Certificado: {'Sí' if result.get('has_custom_certificate') else 'No'}")
                    logger.info(f"   📝 Updates pendientes: {result.get('pending_update_count', 0)}")
                    if result.get('last_error_date'):
                        logger.warning(f"   ⚠️ Último error: {result.get('last_error_message', 'Unknown')}")
                else:
                    logger.info("ℹ️ Webhook no configurado (modo polling)")
                return True
            else:
                logger.error(f"❌ Error obteniendo webhook: {webhook_info.get('description', 'Unknown')}")
                return False
        else:
            logger.error(f"❌ Error HTTP webhook: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error consultando webhook: {e}")
        return False

def test_bot_basic_functionality():
    """Prueba funcionalidad básica del bot"""
    logger.info("\n🧪 === PRUEBA DE FUNCIONALIDAD BÁSICA ===")
    
    try:
        from bot import MedConnectBot
        
        # Crear instancia del bot
        bot = MedConnectBot()
        logger.info("✅ Bot instanciado correctamente")
        
        # Verificar configuraciones
        if bot.bot_token and bot.sheets_id:
            logger.info("✅ Configuraciones básicas cargadas")
        else:
            logger.error("❌ Configuraciones básicas faltantes")
            return False
            
        # Verificar Google Sheets
        if bot.gc:
            logger.info("✅ Cliente de Google Sheets inicializado")
        else:
            logger.error("❌ Cliente de Google Sheets no disponible")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en funcionalidad básica: {e}")
        return False

def main():
    """Función principal de diagnóstico"""
    logger.info("🏥 === DIAGNÓSTICO DE MEDCONNECT BOT ===")
    logger.info(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    tests = [
        ("Variables de Entorno", test_environment_variables),
        ("Bot de Telegram", test_telegram_bot),
        ("Google Sheets", test_google_sheets),
        ("Webhook", test_webhook_url),
        ("Funcionalidad Básica", test_bot_basic_functionality)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ Error ejecutando {test_name}: {e}")
            results[test_name] = False
    
    # Resumen final
    logger.info("\n📋 === RESUMEN DE DIAGNÓSTICO ===")
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        logger.info("\n🎉 ¡Todos los tests pasaron! El bot debería funcionar correctamente.")
    else:
        logger.error("\n⚠️ Algunos tests fallaron. Revisa los errores arriba.")
        
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 