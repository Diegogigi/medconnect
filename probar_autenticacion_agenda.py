#!/usr/bin/env python3
"""
Script para probar la autenticación y el endpoint de agenda
"""

import requests
import json
from datetime import datetime


def probar_autenticacion_y_agenda():
    """Probar el flujo completo de autenticación y agenda"""

    base_url = "http://localhost:8000"
    session = requests.Session()

    print("🔐 Probando autenticación y agenda...")
    print("=" * 50)

    # 1. Verificar que la aplicación esté funcionando
    print("1. Verificando estado de la aplicación...")
    try:
        response = session.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Aplicación funcionando: {data['status']}")
            print(f"   📊 Modo: {data['mode']}")
            print(f"   🗄️ Base de datos: {data['database']}")
        else:
            print(f"   ❌ Error en health check: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error conectando a la aplicación: {e}")
        return

    # 2. Probar endpoint de agenda sin autenticación
    print("\n2. Probando endpoint de agenda sin autenticación...")
    try:
        response = session.get(
            f"{base_url}/api/professional/schedule?fecha=2025-01-15&vista=diaria"
        )
        print(f"   📊 Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correcto: Endpoint requiere autenticación")
        else:
            print(f"   ⚠️ Respuesta inesperada: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 3. Probar login
    print("\n3. Probando login...")
    login_data = {"email": "diego.castro.lagos@gmail.com", "password": "password123"}

    try:
        response = session.post(f"{base_url}/login", data=login_data)
        print(f"   📊 Status: {response.status_code}")

        if response.status_code == 200:
            print("   ✅ Login exitoso")

            # 4. Probar endpoint de agenda con autenticación
            print("\n4. Probando endpoint de agenda con autenticación...")
            response = session.get(
                f"{base_url}/api/professional/schedule?fecha=2025-01-15&vista=diaria"
            )
            print(f"   📊 Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("   ✅ Agenda cargada exitosamente")
                print(f"   📅 Fecha: {data.get('fecha', 'N/A')}")
                print(f"   👁️ Vista: {data.get('vista', 'N/A')}")
                print(f"   📋 Citas: {len(data.get('agenda', []))}")

                if data.get("agenda"):
                    print("   📝 Primeras citas:")
                    for i, cita in enumerate(data["agenda"][:3]):
                        print(
                            f"      {i+1}. {cita.get('hora', 'N/A')} - {cita.get('paciente', 'N/A')}"
                        )
            else:
                print(f"   ❌ Error en agenda: {response.text[:200]}")
        else:
            print(f"   ❌ Error en login: {response.text[:200]}")

    except Exception as e:
        print(f"   ❌ Error en login: {e}")

    print("\n" + "=" * 50)
    print("🧪 Pruebas completadas")


if __name__ == "__main__":
    probar_autenticacion_y_agenda()
