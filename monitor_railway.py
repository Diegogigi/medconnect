#!/usr/bin/env python3
"""
Script para monitorear el estado de Railway
"""

import requests
import time
from datetime import datetime


def monitor_railway():
    """Monitorea el estado de Railway"""

    print("🔍 Monitoreando estado de Railway...")
    print("=" * 50)

    base_url = "https://www.medconnect.cl"
    max_attempts = 10
    attempt = 1

    while attempt <= max_attempts:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n⏰ Intento {attempt}/{max_attempts} - {timestamp}")

        try:
            # Probar health check primero
            response = requests.get(f"{base_url}/health", timeout=5)

            if response.status_code == 200:
                print("🎉 ¡Railway está funcionando!")
                print("✅ Health check responde correctamente")

                # Probar página principal
                main_response = requests.get(base_url, timeout=5)
                if main_response.status_code == 200:
                    print("✅ Página principal funciona")
                    print("🌐 La aplicación está completamente operativa")
                    break
                else:
                    print(f"⚠️ Página principal: {main_response.status_code}")
            else:
                print(f"⚠️ Health check: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")

        if attempt < max_attempts:
            print("⏳ Esperando 30 segundos...")
            time.sleep(30)

        attempt += 1

    if attempt > max_attempts:
        print("\n⚠️ Railway aún no responde después de todos los intentos")
        print("🔧 Posibles causas:")
        print("   - El redeploy está tomando más tiempo del esperado")
        print("   - Hay algún otro error en el código")
        print("   - Las variables de entorno no están configuradas correctamente")
        print("\n💡 Recomendaciones:")
        print("   1. Verifica los logs de Railway")
        print("   2. Confirma que las variables de entorno estén configuradas")
        print("   3. Intenta nuevamente en unos minutos")


if __name__ == "__main__":
    monitor_railway()
