#!/usr/bin/env python3
"""
Script para verificar el estado actual de la aplicación en Railway
"""

import requests
import json


def check_railway_status():
    """Verifica el estado de la aplicación en Railway"""

    print("🔍 Verificando estado de MedConnect en Railway...")
    print("=" * 60)

    # URLs a verificar
    urls_to_check = [
        "https://www.medconnect.cl",
        "https://www.medconnect.cl/api/health",
        "https://www.medconnect.cl/login",
    ]

    for url in urls_to_check:
        print(f"\n🌐 Verificando: {url}")
        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                print(f"  ✅ Status: {response.status_code} - OK")

                # Si es el health endpoint, mostrar detalles
                if "/api/health" in url:
                    try:
                        health_data = response.json()
                        print(f"  📊 Database: {health_data.get('database', 'N/A')}")
                        print(f"  📊 Mode: {health_data.get('mode', 'N/A')}")
                        print(f"  📊 Status: {health_data.get('status', 'N/A')}")
                    except:
                        print(f"  📄 Response: {response.text[:100]}...")
                else:
                    print(
                        f"  📄 Content-Type: {response.headers.get('Content-Type', 'N/A')}"
                    )
                    print(
                        f"  📄 Content-Length: {response.headers.get('Content-Length', 'N/A')}"
                    )

            else:
                print(f"  ❌ Status: {response.status_code} - ERROR")
                print(f"  📄 Response: {response.text[:200]}...")

        except requests.exceptions.Timeout:
            print(f"  ⏰ Timeout - La aplicación no responde")
        except requests.exceptions.ConnectionError:
            print(f"  🔌 Connection Error - No se puede conectar")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    print("\n" + "=" * 60)
    print("📋 Resumen de verificación:")
    print("1. Si todas las URLs responden 200: ✅ Aplicación funcionando")
    print("2. Si hay errores 500: ❌ Problema de configuración")
    print("3. Si hay timeouts: ⏰ Aplicación no está ejecutándose")
    print("4. Si hay errores 404: 🔍 Rutas no encontradas")

    print("\n🔧 Próximos pasos si hay problemas:")
    print("1. Configura las variables en Railway Dashboard")
    print("2. Verifica los logs de Railway")
    print("3. Ejecuta los scripts de solución creados")


if __name__ == "__main__":
    check_railway_status()
