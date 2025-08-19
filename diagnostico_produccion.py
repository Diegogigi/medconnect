#!/usr/bin/env python3
"""
Script para diagnosticar el problema en producción
Verificar si la API key está configurada correctamente en Railway
"""

import os
import requests
import json
from datetime import datetime


def check_production_environment():
    """Verificar el entorno de producción"""
    print("🔍 Diagnóstico de Producción - Railway")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Verificar variables de entorno
    print("📋 Verificando variables de entorno...")
    print("=" * 50)

    env_vars = [
        "RAILWAY_ENVIRONMENT",
        "RAILWAY_STATIC_URL",
        "DOMAIN",
        "FLASK_ENV",
        "OPENROUTER_API_KEY",
    ]

    for var in env_vars:
        value = os.getenv(var)
        if value:
            if var == "OPENROUTER_API_KEY":
                masked_value = (
                    f"{value[:10]}...{value[-10:]}" if len(value) > 20 else "***"
                )
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NO CONFIGURADA")

    return os.getenv("OPENROUTER_API_KEY")


def test_production_api_key():
    """Probar la API key en producción"""
    print("\n🔗 Probando API key de producción...")
    print("=" * 50)

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("❌ OPENROUTER_API_KEY no está configurada en Railway")
        return False, None

    # Probar con la nueva API key
    new_api_key = (
        "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"
    )

    if api_key == new_api_key:
        print("✅ API key correcta configurada")
    else:
        print(f"❌ API key incorrecta: {api_key[:10]}...{api_key[-10:]}")
        print(f"   Debería ser: {new_api_key[:10]}...{new_api_key[-10:]}")
        return False, api_key

    # Probar conexión
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "deepseek/deepseek-r1:free",
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
            print("✅ Conexión exitosa con OpenRouter")
            return True, api_key
        else:
            print(f"❌ Error de conexión: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            return False, api_key

    except Exception as e:
        print(f"❌ Error probando conexión: {e}")
        return False, api_key


def check_railway_deployment():
    """Verificar el despliegue en Railway"""
    print("\n🚂 Verificando despliegue en Railway...")
    print("=" * 50)

    # Obtener URL del servicio
    railway_url = os.getenv("RAILWAY_STATIC_URL") or os.getenv("DOMAIN")

    if not railway_url:
        print("❌ No se pudo determinar la URL del servicio")
        return False

    if not railway_url.startswith(("http://", "https://")):
        railway_url = f"https://{railway_url}"

    print(f"🌐 URL del servicio: {railway_url}")

    try:
        # Probar health check
        health_url = f"{railway_url}/health"
        print(f"🔍 Probando: {health_url}")

        response = requests.get(health_url, timeout=10)

        if response.status_code == 200:
            print("✅ Health check exitoso")

            # Probar endpoint de chat
            chat_url = f"{railway_url}/api/copilot/chat"
            print(f"🔍 Probando endpoint de chat...")

            test_payload = {"message": "Test de conexión", "context": {}}

            chat_response = requests.post(chat_url, json=test_payload, timeout=30)

            if chat_response.status_code == 200:
                print("✅ Endpoint de chat funcionando")
                return True
            else:
                print(f"❌ Endpoint de chat: {chat_response.status_code}")
                print(f"   Respuesta: {chat_response.text[:200]}")
                return False
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error verificando Railway: {e}")
        return False


def generate_railway_fix_instructions():
    """Generar instrucciones para arreglar Railway"""
    print("\n🔧 INSTRUCCIONES PARA ARREGLAR RAILWAY")
    print("=" * 50)

    print("1️⃣ Ir a Railway Dashboard:")
    print("   https://railway.app/dashboard")

    print("\n2️⃣ Seleccionar proyecto MedConnect")

    print("\n3️⃣ Ir a la pestaña 'Variables'")

    print("\n4️⃣ Buscar y actualizar OPENROUTER_API_KEY:")
    print("   - Si existe: Actualizar el valor")
    print("   - Si no existe: Crear nueva variable")
    print("   - Nombre: OPENROUTER_API_KEY")
    print(
        "   - Valor: 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"
    )

    print("\n5️⃣ Verificar otras variables:")
    print("   - RAILWAY_ENVIRONMENT = production")
    print("   - FLASK_ENV = production")
    print("   - SECRET_KEY = [tu-clave-secreta]")

    print("\n6️⃣ Hacer redeploy:")
    print("   - Click en 'Deploy'")
    print("   - Esperar que termine el despliegue")
    print("   - Verificar logs")

    print("\n7️⃣ Probar la aplicación:")
    print("   - Ir a la URL de Railway")
    print("   - Probar el chat de Copilot Health")
    print("   - Verificar que no aparezcan errores")


def main():
    """Función principal"""
    print("🚀 Diagnóstico de Problema en Producción")
    print("=" * 60)

    # 1. Verificar entorno
    current_api_key = check_production_environment()

    # 2. Probar API key
    api_ok, api_key = test_production_api_key()

    # 3. Verificar Railway
    railway_ok = check_railway_deployment()

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)

    if api_ok and railway_ok:
        print("✅ TODO FUNCIONANDO CORRECTAMENTE")
        print("   - API key configurada y funcionando")
        print("   - Railway desplegado correctamente")
    elif api_ok:
        print("⚠️ API key OK, pero Railway puede tener problemas")
    elif railway_ok:
        print("⚠️ Railway OK, pero API key no configurada")
    else:
        print("❌ PROBLEMAS DETECTADOS")
        print("   - API key no configurada o incorrecta")
        print("   - Railway puede tener problemas")

    print("\n🔧 PROBLEMA PRINCIPAL:")
    if not current_api_key:
        print("   ❌ OPENROUTER_API_KEY no está configurada en Railway")
        print(
            "   💡 La aplicación está usando la API key hardcodeada (que puede estar expirada)"
        )
    elif not api_ok:
        print("   ❌ API key configurada pero no funciona")
        print("   💡 Verificar que sea la correcta")
    else:
        print("   ✅ API key configurada correctamente")

    print("\n💡 SOLUCIÓN:")
    if not current_api_key or not api_ok:
        generate_railway_fix_instructions()
    else:
        print("   - El problema puede estar en otro lugar")
        print("   - Verificar logs de Railway")
        print("   - Revisar configuración de la aplicación")

    print("=" * 60)


if __name__ == "__main__":
    main()
