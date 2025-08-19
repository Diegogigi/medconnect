#!/usr/bin/env python3
"""
Script para diagnosticar y solucionar problemas de conexión con OpenRouter
"""

import os
import requests
import json
from datetime import datetime


def check_current_configuration():
    """Verificar la configuración actual"""
    print("🔍 Verificando configuración actual...")
    print("=" * 50)

    # Verificar si estamos en Railway
    railway_env = os.getenv("RAILWAY_ENVIRONMENT")
    if railway_env:
        print(f"✅ Ejecutando en Railway: {railway_env}")
    else:
        print("⚠️ No detectado como entorno Railway")

    # Verificar API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        print(f"✅ OPENROUTER_API_KEY configurada: {api_key[:10]}...{api_key[-10:]}")
        return api_key
    else:
        print("❌ OPENROUTER_API_KEY no configurada")
        return None


def test_openrouter_with_fallback():
    """Probar OpenRouter con fallback a API key hardcodeada"""
    print("\n🔗 Probando conexión con OpenRouter...")
    print("=" * 50)

    # API key hardcodeada como fallback
    fallback_api_key = (
        "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"
    )

    # Intentar con API key de entorno primero
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("⚠️ Usando API key de fallback...")
        api_key = fallback_api_key

    models_to_test = [
        "deepseek/deepseek-r1:free",
        "openai/gpt-3.5-turbo",
        "anthropic/claude-3-haiku",
    ]

    for model in models_to_test:
        print(f"🔧 Probando modelo: {model}")

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Eres un asistente de prueba. Responde solo 'OK' si recibes este mensaje.",
                    },
                    {"role": "user", "content": "Test de conexión"},
                ],
                "max_tokens": 10,
                "temperature": 0.1,
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )

            if response.status_code == 200:
                print(f"✅ {model}: Conexión exitosa")
                return True, api_key, model
            else:
                print(f"❌ {model}: Error {response.status_code}")
                print(f"   Respuesta: {response.text[:200]}")

        except Exception as e:
            print(f"❌ {model}: Error de conexión - {e}")

    return False, None, None


def check_railway_variables():
    """Verificar variables de Railway"""
    print("\n🚂 Verificando variables de Railway...")
    print("=" * 50)

    railway_vars = [
        "RAILWAY_ENVIRONMENT",
        "RAILWAY_STATIC_URL",
        "DOMAIN",
        "FLASK_ENV",
        "SECRET_KEY",
    ]

    for var in railway_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: No configurada")

    return os.getenv("RAILWAY_ENVIRONMENT") is not None


def generate_railway_config_instructions():
    """Generar instrucciones para configurar Railway"""
    print("\n📋 INSTRUCCIONES PARA CONFIGURAR RAILWAY")
    print("=" * 50)

    print("1️⃣ Ir a Railway Dashboard:")
    print("   https://railway.app/dashboard")

    print("\n2️⃣ Seleccionar tu proyecto MedConnect")

    print("\n3️⃣ Ir a la pestaña 'Variables'")

    print("\n4️⃣ Agregar las siguientes variables:")
    print(
        "   OPENROUTER_API_KEY = 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"
    )
    print("   RAILWAY_ENVIRONMENT = production")
    print("   FLASK_ENV = production")
    print("   SECRET_KEY = tu-clave-secreta-super-segura-aqui")

    print("\n5️⃣ Hacer click en 'Deploy' para aplicar los cambios")

    print("\n6️⃣ Esperar que el deploy termine y verificar los logs")


def test_local_app_endpoints():
    """Probar endpoints locales de la aplicación"""
    print("\n🔌 Probando endpoints locales...")
    print("=" * 50)

    try:
        # Intentar conectar al servidor local
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor local funcionando")

            # Probar endpoint de chat
            test_payload = {"message": "Test de conexión", "context": {}}

            chat_response = requests.post(
                "http://localhost:5000/api/copilot/chat", json=test_payload, timeout=10
            )

            if chat_response.status_code == 200:
                print("✅ Endpoint de chat funcionando")
                return True
            else:
                print(f"❌ Endpoint de chat: {chat_response.status_code}")
                return False
        else:
            print(f"❌ Servidor local: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error conectando al servidor local: {e}")
        return False


def create_env_file():
    """Crear archivo .env local para desarrollo"""
    print("\n📝 Creando archivo .env local...")
    print("=" * 50)

    env_content = """# MedConnect - Variables de Entorno Local
# Copia este archivo como .env y completa con tus valores reales

# Configuración de Flask
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=clave-secreta-local-desarrollo

# Configuración del dominio
DOMAIN=localhost:5000
BASE_URL=http://localhost:5000

# Configuración de OpenRouter (API key de fallback)
OPENROUTER_API_KEY=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

# Configuración de logging
LOG_LEVEL=INFO

# Configuración de Railway (para producción)
PORT=5000
RAILWAY_ENVIRONMENT=development
"""

    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✅ Archivo .env creado exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error creando .env: {e}")
        return False


def main():
    """Función principal"""
    print("🚀 Diagnóstico y Solución de Problemas OpenRouter")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Verificar configuración actual
    current_api_key = check_current_configuration()

    # 2. Verificar si estamos en Railway
    is_railway = check_railway_variables()

    # 3. Probar conexión OpenRouter
    connection_ok, working_api_key, working_model = test_openrouter_with_fallback()

    # 4. Probar endpoints locales
    local_ok = test_local_app_endpoints()

    # Resumen y recomendaciones
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)

    if connection_ok:
        print("✅ OpenRouter conectado correctamente")
        print(f"   - API Key: {working_api_key[:10]}...{working_api_key[-10:]}")
        print(f"   - Modelo funcionando: {working_model}")
    else:
        print("❌ Problemas con OpenRouter")

    if is_railway:
        print("✅ Ejecutando en Railway")
    else:
        print("⚠️ Ejecutando localmente")

    if local_ok:
        print("✅ Servidor local funcionando")
    else:
        print("❌ Problemas con servidor local")

    print("\n🔧 RECOMENDACIONES:")

    if not connection_ok:
        print("   1. Verificar conectividad de red")
        print("   2. Comprobar que OpenRouter esté disponible")
        print("   3. Verificar límites de uso de la API")

    if is_railway and not current_api_key:
        print("   4. Configurar OPENROUTER_API_KEY en Railway")
        generate_railway_config_instructions()

    if not is_railway and not os.path.exists(".env"):
        print("   5. Crear archivo .env para desarrollo local")
        create_env_file()

    if not local_ok:
        print("   6. Iniciar servidor local: python app.py")

    print("\n💡 SOLUCIÓN RÁPIDA:")
    if connection_ok:
        print("   - El problema puede estar en la configuración de Railway")
        print("   - Verificar que OPENROUTER_API_KEY esté configurada")
        print("   - Hacer redeploy en Railway después de configurar variables")
    else:
        print("   - Usar la API key de fallback temporalmente")
        print("   - Verificar conectividad de red")
        print("   - Contactar soporte de OpenRouter si persiste")

    print("=" * 60)


if __name__ == "__main__":
    main()
