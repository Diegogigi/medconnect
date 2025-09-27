#!/usr/bin/env python3
"""
Script para verificar el despliegue en Railway
"""

import requests
import time
import json


def verify_railway_deployment():
    """Verifica que el despliegue en Railway esté funcionando"""

    print("🔍 Verificando despliegue en Railway...")
    print("=" * 60)

    # URLs a verificar
    urls_to_check = [
        {
            "url": "https://www.medconnect.cl",
            "name": "Página Principal",
            "expected_status": 200,
        },
        {
            "url": "https://www.medconnect.cl/login",
            "name": "Página de Login",
            "expected_status": 200,
        },
        {
            "url": "https://www.medconnect.cl/api/health",
            "name": "Health Endpoint",
            "expected_status": 200,
        },
    ]

    print("⏳ Esperando que Railway procese el despliegue...")
    print("🔧 Esto puede tomar 2-3 minutos...")

    # Esperar un poco para que Railway procese
    time.sleep(30)

    results = []

    for check in urls_to_check:
        print(f"\n🌐 Verificando: {check['name']}")
        print(f"   URL: {check['url']}")

        try:
            response = requests.get(check["url"], timeout=15)

            if response.status_code == check["expected_status"]:
                print(f"  ✅ Status: {response.status_code} - OK")
                results.append(True)

                # Información adicional para health endpoint
                if "/api/health" in check["url"]:
                    try:
                        health_data = response.json()
                        print(f"  📊 Database: {health_data.get('database', 'N/A')}")
                        print(f"  📊 Mode: {health_data.get('mode', 'N/A')}")
                        print(f"  📊 Status: {health_data.get('status', 'N/A')}")
                    except:
                        print(f"  📄 Response: {response.text[:100]}...")

            else:
                print(f"  ❌ Status: {response.status_code} - ERROR")
                print(f"  📄 Response: {response.text[:200]}...")
                results.append(False)

        except requests.exceptions.Timeout:
            print(f"  ⏰ Timeout - La aplicación no responde")
            results.append(False)
        except requests.exceptions.ConnectionError:
            print(f"  🔌 Connection Error - No se puede conectar")
            results.append(False)
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append(False)

    # Resumen de verificación
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE VERIFICACIÓN:")

    success_count = sum(results)
    total_count = len(results)

    if success_count == total_count:
        print("🎉 ¡TODAS LAS VERIFICACIONES EXITOSAS!")
        print("✅ El despliegue en Railway está funcionando correctamente")

        print("\n🔧 PRÓXIMOS PASOS:")
        print("1. Configura las variables de entorno en Railway Dashboard")
        print("2. Ejecuta los scripts de migración de usuarios")
        print("3. Prueba el login con las credenciales de prueba")

    elif success_count > 0:
        print(f"⚠️ VERIFICACIÓN PARCIAL: {success_count}/{total_count} exitosas")
        print("🔧 Algunos endpoints funcionan, otros necesitan configuración")

        print("\n🔧 ACCIONES RECOMENDADAS:")
        print("1. Configura las variables de entorno en Railway")
        print("2. Revisa los logs de Railway para errores")
        print("3. Espera unos minutos y vuelve a verificar")

    else:
        print("❌ VERIFICACIÓN FALLIDA: Ningún endpoint responde correctamente")
        print("🔧 El despliegue puede estar fallando")

        print("\n🔧 ACCIONES RECOMENDADAS:")
        print("1. Revisa los logs de Railway Dashboard")
        print("2. Verifica que las variables de entorno estén configuradas")
        print("3. Espera más tiempo para que Railway procese el despliegue")
        print("4. Contacta soporte de Railway si persiste el problema")

    return success_count == total_count


def show_railway_config_instructions():
    """Muestra instrucciones para configurar Railway"""

    print("\n📋 CONFIGURACIÓN REQUERIDA EN RAILWAY:")
    print("=" * 50)

    print("\n1️⃣ Ve a Railway Dashboard:")
    print("   https://railway.app/dashboard")

    print("\n2️⃣ Selecciona tu proyecto MedConnect")

    print("\n3️⃣ Ve a la pestaña 'Variables'")

    print("\n4️⃣ Agrega estas variables (CRÍTICAS):")
    print()
    print("   DATABASE_URL")
    print(
        "   = postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"
    )
    print()
    print("   SECRET_KEY")
    print("   = medconnect-secret-key-2025-railway-production-ultra-secure")
    print()
    print("   FLASK_ENV")
    print("   = production")
    print()
    print("   OPENROUTER_API_KEY")
    print(
        "   = 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"
    )
    print()
    print("   PORT")
    print("   = 5000")

    print("\n5️⃣ Guarda los cambios")
    print("   Railway redeployeará automáticamente")

    print("\n6️⃣ Espera 2-3 minutos y vuelve a verificar")


if __name__ == "__main__":
    print("🚀 VERIFICACIÓN DESPLIEGUE RAILWAY")
    print("=" * 60)

    success = verify_railway_deployment()

    if not success:
        show_railway_config_instructions()

    print("\n🎯 RESULTADO FINAL:")
    if success:
        print("✅ Despliegue exitoso - Aplicación funcionando")
    else:
        print("⚠️ Despliegue necesita configuración adicional")
        print("🔧 Sigue las instrucciones de configuración")
