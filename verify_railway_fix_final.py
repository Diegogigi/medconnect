#!/usr/bin/env python3
"""
Script final para verificar que Railway esté funcionando
"""

import requests
import time


def verify_railway_fix_final():
    """Verifica que Railway esté funcionando correctamente"""

    print("🔍 Verificación final de Railway...")
    print("=" * 50)

    # URL de Railway
    base_url = "https://www.medconnect.cl"

    print(f"🌐 Verificando: {base_url}")
    print()

    # Pruebas a realizar
    tests = [
        ("/", "Página principal"),
        ("/health", "Health check"),
        ("/favicon.ico", "Favicon"),
        ("/login", "Página de login"),
    ]

    all_passed = True

    for endpoint, description in tests:
        url = f"{base_url}{endpoint}"
        print(f"🧪 Probando {description}...")

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {description}: OK (200)")
            elif response.status_code == 204:
                print(f"  ✅ {description}: OK (204 - No content)")
            else:
                print(f"  ⚠️ {description}: {response.status_code}")
                all_passed = False
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {description}: Error - {e}")
            all_passed = False

        time.sleep(1)  # Pausa entre requests

    print()
    print("=" * 50)

    if all_passed:
        print("🎉 ¡Railway está funcionando correctamente!")
        print("✅ Todos los endpoints responden correctamente")
        print("🌐 La aplicación está disponible en www.medconnect.cl")
        print()
        print("📝 Próximos pasos:")
        print("1. Prueba el login con los usuarios de prueba")
        print("2. Verifica las funcionalidades de la aplicación")
        print("3. El desarrollo local sigue disponible en http://localhost:5000")
    else:
        print("⚠️ Algunos problemas detectados")
        print("🔧 Railway puede estar aún redeployando")
        print("⏰ Espera 2-3 minutos y vuelve a probar")

    return all_passed


if __name__ == "__main__":
    verify_railway_fix_final()
