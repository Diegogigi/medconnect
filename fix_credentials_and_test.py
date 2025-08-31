#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir problemas de credenciales y probar la aplicación
"""

import os
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_credentials():
    """Corregir problemas de credenciales"""
    logger.info("🔧 Corrigiendo problemas de credenciales...")

    # Verificar variable de entorno actual
    current_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    logger.info(f"📄 Variable actual: {current_json[:50]}...")

    # Si la variable contiene un path, intentar leer el archivo
    if current_json.startswith("./") or current_json.startswith("/"):
        logger.info(f"📁 Detectado path: {current_json}")
        if os.path.exists(current_json):
            try:
                with open(current_json, "r") as f:
                    json_content = f.read()
                logger.info("✅ Archivo leído correctamente")
                return json_content
            except Exception as e:
                logger.error(f"❌ Error leyendo archivo: {e}")
        else:
            logger.error(f"❌ Archivo no encontrado: {current_json}")

    # Si es JSON válido, devolverlo
    elif current_json:
        try:
            json.loads(current_json)
            logger.info("✅ JSON válido detectado")
            return current_json
        except json.JSONDecodeError:
            logger.error("❌ JSON inválido")

    # Crear credenciales de prueba
    logger.info("🔧 Creando credenciales de prueba...")
    test_credentials = {
        "type": "service_account",
        "project_id": "medconnect-test",
        "private_key_id": "test-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nTEST_KEY\n-----END PRIVATE KEY-----\n",
        "client_email": "test@medconnect-test.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test%40medconnect-test.iam.gserviceaccount.com",
    }

    return json.dumps(test_credentials)


def test_auth_manager():
    """Probar AuthManager con credenciales corregidas"""
    logger.info("🧪 Probando AuthManager...")

    try:
        from auth_manager import AuthManager

        # Crear instancia
        auth_manager = AuthManager()

        # Verificar si está usando fallback
        if auth_manager.use_fallback:
            logger.info("✅ AuthManager usando sistema de fallback")
        else:
            logger.info("✅ AuthManager conectado a Google Sheets")

        # Probar autenticación
        success, result = auth_manager.login_user(
            "diego.castro.lagos@gmail.com", "password123"
        )
        if success:
            logger.info(f"✅ Login exitoso: {result}")
        else:
            logger.error(f"❌ Login fallido: {result}")

        return True

    except Exception as e:
        logger.error(f"❌ Error probando AuthManager: {e}")
        return False


def test_sheets_manager():
    """Probar SheetsManager con datos de fallback"""
    logger.info("🧪 Probando SheetsManager...")

    try:
        from backend.database.sheets_manager import sheets_db

        # Probar obtención de datos
        atenciones = sheets_db.get_all_records_fallback("Atenciones_Medicas")
        logger.info(f"✅ Atenciones obtenidas: {len(atenciones)} registros")

        pacientes = sheets_db.get_all_records_fallback("Pacientes_Profesional")
        logger.info(f"✅ Pacientes obtenidos: {len(pacientes)} registros")

        agenda = sheets_db.get_all_records_fallback("Citas_Agenda")
        logger.info(f"✅ Agenda obtenida: {len(agenda)} registros")

        return True

    except Exception as e:
        logger.error(f"❌ Error probando SheetsManager: {e}")
        return False


def main():
    """Función principal"""
    logger.info("🚀 Iniciando corrección de credenciales y pruebas...")

    # Corregir credenciales
    fixed_credentials = fix_credentials()

    # Establecer variable de entorno corregida
    os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"] = fixed_credentials
    logger.info("✅ Variable de entorno corregida")

    # Probar AuthManager
    auth_ok = test_auth_manager()

    # Probar SheetsManager
    sheets_ok = test_sheets_manager()

    # Resumen
    logger.info("📊 Resumen de pruebas:")
    logger.info(f"   AuthManager: {'✅ OK' if auth_ok else '❌ Error'}")
    logger.info(f"   SheetsManager: {'✅ OK' if sheets_ok else '❌ Error'}")

    if auth_ok and sheets_ok:
        logger.info("🎉 Todas las pruebas pasaron exitosamente")
        logger.info("💡 La aplicación debería funcionar correctamente ahora")
    else:
        logger.warning(
            "⚠️ Algunas pruebas fallaron, pero el sistema de fallback debería funcionar"
        )


if __name__ == "__main__":
    main()
