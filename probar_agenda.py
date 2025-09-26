#!/usr/bin/env python3
"""
Script para probar las APIs de agenda
"""

import requests
import json


def probar_apis_agenda():
    """Prueba las APIs de agenda"""

    print("🧪 Probando APIs de agenda...")
    print("=" * 60)

    base_url = "http://localhost:8000"

    # URLs a probar
    apis_agenda = [
        "/api/professional/schedule?fecha=2025-09-07&vista=diaria",
        "/api/agenda?fecha=2025-09-07",
        "/api/citas",
        "/api/schedule",
    ]

    for api_url in apis_agenda:
        url = f"{base_url}{api_url}"
        print(f"\n🔍 Probando: {api_url}")

        try:
            response = requests.get(url, timeout=5)
            print(f"  📊 Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Success: {data.get('success', 'N/A')}")
                print(f"  📋 Total: {data.get('total', 'N/A')}")
                print(f"  📅 Fecha: {data.get('fecha', 'N/A')}")

                if "data" in data and data["data"]:
                    print(
                        f"  👥 Primer elemento: {data['data'][0].get('paciente_nombre', 'N/A')}"
                    )
            else:
                print(f"  ❌ Error: {response.status_code}")
                print(f"  📄 Response: {response.text[:100]}...")

        except requests.exceptions.ConnectionError:
            print(f"  ❌ Error: No se puede conectar a {url}")
            print(f"  💡 Asegúrate de que la aplicación esté ejecutándose")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    print("\n" + "=" * 60)
    print("🧪 Pruebas de agenda completadas")


def main():
    """Función principal"""
    try:
        probar_apis_agenda()
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")


if __name__ == "__main__":
    main()
