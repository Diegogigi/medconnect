#!/usr/bin/env python3
"""
Script para verificar el estado de las variables de entorno en Railway
Especialmente para la configuración de OpenRouter API
"""

import os
import requests
import json
from datetime import datetime


def check_environment_variables():
    """Verificar variables de entorno críticas"""
    print("🔍 Verificando variables de entorno...")
    print("=" * 50)

    # Variables críticas para OpenRouter
    critical_vars = [
        "OPENROUTER_API_KEY",
        "RAILWAY_ENVIRONMENT",
        "FLASK_ENV",
        "SECRET_KEY",
    ]

    for var in critical_vars:
        value = os.getenv(var)
        if value:
            if var == "OPENROUTER_API_KEY":
                # Mostrar solo los primeros y últimos caracteres por seguridad
                masked_value = (
                    f"{value[:10]}...{value[-10:]}" if len(value) > 20 else "***"
                )
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: Configurada")
        else:
            print(f"❌ {var}: NO CONFIGURADA")

    print("\n" + "=" * 50)


def test_openrouter_connection():
    """Probar conexión con OpenRouter"""
    print("🔗 Probando conexión con OpenRouter...")
    print("=" * 50)

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("❌ OPENROUTER_API_KEY no está configurada")
        return False

    try:
        # Probar con diferentes modelos
        models_to_test = [
            "deepseek/deepseek-r1:free",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-haiku",
        ]

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        for model in models_to_test:
            print(f"🔧 Probando modelo: {model}")

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
                return True
            else:
                print(f"❌ {model}: Error {response.status_code}")
                print(f"   Respuesta: {response.text[:200]}")

    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

    return False


def test_railway_health():
    """Verificar salud del servicio en Railway"""
    print("🚂 Verificando salud del servicio Railway...")
    print("=" * 50)

    try:
        # Intentar obtener la URL del servicio
        railway_url = os.getenv("RAILWAY_STATIC_URL") or os.getenv("DOMAIN")

        if railway_url:
            if not railway_url.startswith(("http://", "https://")):
                railway_url = f"https://{railway_url}"

            print(f"🌐 URL del servicio: {railway_url}")

            # Probar endpoint de health check
            health_url = f"{railway_url}/health"
            print(f"🔍 Probando: {health_url}")

            response = requests.get(health_url, timeout=10)

            if response.status_code == 200:
                print("✅ Health check exitoso")
                return True
            else:
                print(f"❌ Health check falló: {response.status_code}")
                return False
        else:
            print("❌ No se pudo determinar la URL del servicio")
            return False

    except Exception as e:
        print(f"❌ Error verificando Railway: {e}")
        return False


def check_api_endpoints():
    """Verificar endpoints de la API"""
    print("🔌 Verificando endpoints de la API...")
    print("=" * 50)

    try:
        railway_url = os.getenv("RAILWAY_STATIC_URL") or os.getenv("DOMAIN")

        if not railway_url:
            print("❌ No se pudo determinar la URL del servicio")
            return

        if not railway_url.startswith(("http://", "https://")):
            railway_url = f"https://{railway_url}"

        endpoints = [
            "/api/copilot/chat",
            "/api/copilot/orchestrate",
            "/api/search-scientific-papers",
        ]

        for endpoint in endpoints:
            url = f"{railway_url}{endpoint}"
            print(f"🔍 Probando: {endpoint}")

            try:
                response = requests.get(url, timeout=5)
                if (
                    response.status_code == 405
                ):  # Method Not Allowed (esperado para POST)
                    print(f"✅ {endpoint}: Endpoint disponible (POST requerido)")
                elif response.status_code == 200:
                    print(f"✅ {endpoint}: Endpoint disponible")
                else:
                    print(f"⚠️ {endpoint}: Status {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint}: Error - {e}")

    except Exception as e:
        print(f"❌ Error verificando endpoints: {e}")


def main():
    """Función principal"""
    print("🚀 Diagnóstico de Railway y OpenRouter")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Verificar variables de entorno
    check_environment_variables()

    # 2. Probar conexión OpenRouter
    openrouter_ok = test_openrouter_connection()

    # 3. Verificar Railway
    railway_ok = test_railway_health()

    # 4. Verificar endpoints
    check_api_endpoints()

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)

    if openrouter_ok and railway_ok:
        print("✅ TODO FUNCIONANDO CORRECTAMENTE")
        print("   - Variables de entorno configuradas")
        print("   - OpenRouter conectado")
        print("   - Railway funcionando")
    elif openrouter_ok:
        print("⚠️ OpenRouter OK, pero Railway puede tener problemas")
    elif railway_ok:
        print("⚠️ Railway OK, pero OpenRouter no conecta")
    else:
        print("❌ PROBLEMAS DETECTADOS")
        print("   - Revisar configuración de Railway")
        print("   - Verificar OPENROUTER_API_KEY")
        print("   - Comprobar conectividad de red")

    print("\n🔧 RECOMENDACIONES:")
    if not os.getenv("OPENROUTER_API_KEY"):
        print("   1. Configurar OPENROUTER_API_KEY en Railway")
        print("   2. Obtener API key desde: https://openrouter.ai/")
    if not railway_ok:
        print("   3. Verificar despliegue en Railway")
        print("   4. Revisar logs de Railway")

    print("=" * 60)


if __name__ == "__main__":
    main()
