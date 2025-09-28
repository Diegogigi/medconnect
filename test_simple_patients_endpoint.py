#!/usr/bin/env python3
"""
Script para probar el nuevo endpoint simplificado de pacientes
"""

import requests
import json


def test_simple_patients_endpoint():
    """Prueba el nuevo endpoint simplificado de pacientes"""

    print("🧪 Probando endpoint simplificado de pacientes...")
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

        # 3. Probar endpoint simplificado de pacientes
        print(f"📋 Probando endpoint simplificado de pacientes...")
        patients_url = "https://www.medconnect.cl/api/professional/patients-simple"
        patients_response = session.get(patients_url)

        print(f"📊 Status: {patients_response.status_code}")
        print(f"📄 Headers: {dict(patients_response.headers)}")

        if patients_response.status_code == 200:
            try:
                data = patients_response.json()
                print(f"✅ Respuesta JSON válida")
                print(f"📊 Success: {data.get('success', 'N/A')}")
                print(f"👥 Pacientes: {len(data.get('pacientes', []))}")

                if data.get("pacientes"):
                    for paciente in data["pacientes"]:
                        print(
                            f"  - {paciente.get('nombre', '')} {paciente.get('apellido', '')} ({paciente.get('email', '')})"
                        )

                return True

            except json.JSONDecodeError:
                print(f"❌ Respuesta no es JSON válido")
                print(f"📄 Contenido: {patients_response.text[:500]}...")
                return False

        elif patients_response.status_code == 500:
            try:
                data = patients_response.json()
                print(f"❌ Error 500: {data.get('error', 'Error desconocido')}")
            except:
                print(f"❌ Error 500: {patients_response.text[:200]}...")
            return False

        else:
            print(f"❌ Error inesperado: {patients_response.status_code}")
            print(f"📄 Respuesta: {patients_response.text[:200]}...")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 PRUEBA ENDPOINT SIMPLIFICADO PACIENTES")
    print("=" * 60)

    success = test_simple_patients_endpoint()

    if success:
        print(f"\n🎉 ¡Endpoint simplificado funciona correctamente!")
        print(f"🔧 Ahora puedes usar este endpoint en lugar del problemático")
    else:
        print(f"\n❌ Error en el endpoint simplificado")
        print(f"🔧 Revisa los logs del servidor")
