#!/usr/bin/env python3
"""
Script para probar el endpoint de agenda
"""

import requests
import json


def test_agenda_endpoint():
    """Probar el endpoint de agenda"""

    print("🧪 Probando endpoint de agenda...")
    print("=" * 60)

    # URL de login
    login_url = "https://www.medconnect.cl/login"

    # Credenciales
    email = "diego.castro.lagos@gmail.com"
    password = "password123"

    try:
        # Crear sesión
        session = requests.Session()

        # 1. Login
        print(f"🔐 Haciendo login...")
        login_data = {"email": email, "password": password}
        login_response = session.post(login_url, data=login_data, allow_redirects=False)

        if login_response.status_code not in [200, 302]:
            print(f"❌ Error en login: {login_response.status_code}")
            return False

        # Verificar si el login fue exitoso revisando el contenido
        if (
            "error" in login_response.text.lower()
            or "invalid" in login_response.text.lower()
        ):
            print(f"❌ Error en credenciales: {login_response.text[:200]}")
            return False

        print(f"✅ Login exitoso")

        # 2. Obtener página profesional para establecer sesión
        print(f"📄 Obteniendo página profesional...")
        professional_url = "https://www.medconnect.cl/professional"
        professional_response = session.get(professional_url)

        if professional_response.status_code != 200:
            print(
                f"❌ Error obteniendo página profesional: {professional_response.status_code}"
            )
            return False

        print(f"✅ Página profesional cargada")

        # 3. Probar endpoint de agenda
        print(f"📅 Probando endpoint de agenda...")
        agenda_url = "https://www.medconnect.cl/api/professional/schedule"
        agenda_response = session.get(agenda_url)

        print(f"📊 Status agenda: {agenda_response.status_code}")
        print(f"📊 Headers: {dict(agenda_response.headers)}")

        if agenda_response.status_code == 200:
            try:
                agenda_data = agenda_response.json()
                print(f"✅ Agenda cargada exitosamente")
                print(f"📊 Datos recibidos: {json.dumps(agenda_data, indent=2)}")
                return True
            except json.JSONDecodeError as e:
                print(f"❌ Error parseando JSON: {e}")
                print(f"📊 Respuesta: {agenda_response.text[:500]}")
                return False
        else:
            print(f"❌ Error en agenda: {agenda_response.text[:500]}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 PRUEBA ENDPOINT AGENDA")
    print("=" * 60)

    success = test_agenda_endpoint()

    if success:
        print(f"\n🎉 ¡Endpoint de agenda funciona correctamente!")
    else:
        print(f"\n❌ Error en endpoint de agenda")
        print(f"🔧 Revisa los logs del servidor")
