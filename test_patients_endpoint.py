#!/usr/bin/env python3
"""
Script para probar el endpoint de pacientes en Railway
"""

import requests
import json


def test_patients_endpoint():
    """Prueba el endpoint de pacientes en Railway"""

    print("🧪 Probando endpoint de pacientes en Railway...")
    print("=" * 60)

    # URL del endpoint
    patients_url = "https://www.medconnect.cl/api/professional/patients"

    # Datos de login para obtener sesión
    login_url = "https://www.medconnect.cl/login"

    # Credenciales de prueba
    test_credentials = [
        {
            "email": "diego.castro.lagos@gmail.com",
            "password": "password123",
            "expected_type": "profesional",
        }
    ]

    for creds in test_credentials:
        print(f"\n🔐 Probando con profesional: {creds['email']}")

        try:
            # Crear sesión
            session = requests.Session()

            # 1. Obtener página de login
            print(f"  📄 Obteniendo página de login...")
            response = session.get(login_url)

            if response.status_code != 200:
                print(f"  ❌ Error obteniendo página de login: {response.status_code}")
                continue

            print(f"  ✅ Página de login cargada correctamente")

            # 2. Intentar login
            print(f"  🔐 Intentando login...")
            login_data = {"email": creds["email"], "password": creds["password"]}

            login_response = session.post(
                login_url, data=login_data, allow_redirects=False
            )

            if login_response.status_code == 302:
                print(f"  ✅ Login exitoso - Redirigiendo")
                redirect_url = login_response.headers.get("Location", "")
                print(f"  📍 Redirigiendo a: {redirect_url}")

                # 3. Probar endpoint de pacientes
                print(f"  📋 Probando endpoint de pacientes...")
                patients_response = session.get(patients_url)

                print(f"  📊 Status del endpoint: {patients_response.status_code}")

                if patients_response.status_code == 200:
                    try:
                        data = patients_response.json()
                        print(f"  ✅ Respuesta JSON válida")
                        print(f"  📊 Success: {data.get('success', 'N/A')}")
                        print(
                            f"  👥 Pacientes encontrados: {len(data.get('pacientes', []))}"
                        )

                        pacientes = data.get("pacientes", [])
                        if pacientes:
                            print(f"  📋 Lista de pacientes:")
                            for i, paciente in enumerate(pacientes, 1):
                                nombre = f"{paciente.get('nombre', '')} {paciente.get('apellido', '')}"
                                email = paciente.get("email", "N/A")
                                estado = paciente.get("estado_relacion", "N/A")
                                print(f"    {i}. {nombre} ({email}) - Estado: {estado}")
                        else:
                            print(f"  📋 No hay pacientes asociados a este profesional")
                            print(f"  💡 Esto es correcto para un profesional nuevo")

                    except json.JSONDecodeError:
                        print(f"  ❌ Respuesta no es JSON válido")
                        print(f"  📄 Respuesta: {patients_response.text[:200]}...")
                else:
                    print(f"  ❌ Error en endpoint: {patients_response.status_code}")
                    print(f"  📄 Respuesta: {patients_response.text[:200]}...")

            else:
                print(f"  ❌ Login fallido: {login_response.status_code}")
                if login_response.status_code == 200:
                    if "Credenciales inválidas" in login_response.text:
                        print(f"  ❌ Credenciales inválidas")
                    else:
                        print(f"  ⚠️ Login no procesado correctamente")

        except Exception as e:
            print(f"  ❌ Error probando endpoint: {e}")

    print(f"\n" + "=" * 60)
    print("📋 Resumen de pruebas:")
    print("1. Si el endpoint devuelve 0 pacientes: ✅ Correcto para profesional nuevo")
    print("2. Si el endpoint devuelve pacientes: ✅ Funcionando correctamente")
    print("3. Si hay errores 500: ❌ Problema de configuración")
    print("4. Si hay errores 401: ❌ Problema de autenticación")


if __name__ == "__main__":
    test_patients_endpoint()
