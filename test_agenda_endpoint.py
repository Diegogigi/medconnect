#!/usr/bin/env python3
"""
Script para probar el endpoint de agenda
"""

import requests
import json


def test_agenda_endpoint():
    """Prueba el endpoint de agenda"""

    print("📅 Probando endpoint de agenda...")
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

        if login_response.status_code != 302:
            print(f"❌ Error en login: {login_response.status_code}")
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

        print(f"📊 Status: {agenda_response.status_code}")
        print(f"📄 Headers: {dict(agenda_response.headers)}")

        if agenda_response.status_code == 200:
            try:
                data = agenda_response.json()
                print(f"✅ Respuesta JSON válida")
                print(f"📊 Success: {data.get('success', 'N/A')}")
                print(f"📅 Agenda: {len(data.get('agenda', []))}")

                if data.get("agenda"):
                    for cita in data["agenda"]:
                        print(
                            f"  - {cita.get('paciente_nombre', '')} - {cita.get('fecha', '')} {cita.get('hora_inicio', '')}"
                        )

                return True

            except json.JSONDecodeError:
                print(f"❌ Respuesta no es JSON válido")
                print(f"📄 Contenido: {agenda_response.text[:500]}...")
                return False

        elif agenda_response.status_code == 500:
            try:
                data = agenda_response.json()
                print(f"❌ Error 500: {data.get('error', 'Error desconocido')}")
            except:
                print(f"❌ Error 500: {agenda_response.text[:200]}...")
            return False

        else:
            print(f"❌ Error inesperado: {agenda_response.status_code}")
            print(f"📄 Respuesta: {agenda_response.text[:200]}...")
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
        print(f"\n❌ Error en el endpoint de agenda")
        print(f"🔧 Revisa los logs del servidor")
