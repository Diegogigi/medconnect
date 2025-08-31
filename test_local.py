#!/usr/bin/env python3
"""
Script para probar funcionalidades localmente
"""

import requests
import json
import time


def test_local_app():
    """Prueba las funcionalidades básicas de la aplicación local"""

    base_url = "http://localhost:5000"

    print("🧪 Probando aplicación local...")
    print(f"   URL base: {base_url}")
    print("-" * 50)

    # Test 1: Página principal
    print("1️⃣ Probando página principal...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ Página principal OK")
            data = response.json()
            print(f"   📝 Mensaje: {data.get('message', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error conectando: {e}")

    # Test 2: Health check
    print("\n2️⃣ Probando health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Health check OK")
            data = response.json()
            print(f"   📊 Estado: {data.get('status', 'N/A')}")
            print(f"   🔗 Auth Manager: {data.get('auth_manager', 'N/A')}")
            print(f"   🗄️ PostgreSQL: {data.get('postgres_connected', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: Robots.txt
    print("\n3️⃣ Probando robots.txt...")
    try:
        response = requests.get(f"{base_url}/robots.txt")
        if response.status_code == 200:
            print("   ✅ Robots.txt OK")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 4: Favicon
    print("\n4️⃣ Probando favicon...")
    try:
        response = requests.get(f"{base_url}/favicon.ico")
        if response.status_code in [200, 204]:
            print("   ✅ Favicon OK")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 5: Login page
    print("\n5️⃣ Probando página de login...")
    try:
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print("   ✅ Página de login OK")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n" + "=" * 50)
    print("🎯 Pruebas completadas")
    print("💡 Para más pruebas, abre http://localhost:5000 en tu navegador")


if __name__ == "__main__":
    test_local_app()
