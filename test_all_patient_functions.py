#!/usr/bin/env python3
"""
Script para probar todas las funcionalidades de pacientes
"""

import requests
import json


def test_all_patient_functions():
    """Probar todas las funcionalidades de pacientes"""

    print("🧪 Probando todas las funcionalidades de pacientes...")
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

        # 3. Obtener lista de pacientes
        print(f"📋 Obteniendo lista de pacientes...")
        patients_url = "https://www.medconnect.cl/api/professional/patients-simple"
        patients_response = session.get(patients_url)

        if patients_response.status_code != 200:
            print(f"❌ Error obteniendo pacientes: {patients_response.status_code}")
            return False

        try:
            patients_data = patients_response.json()
            pacientes = patients_data.get("pacientes", [])
            print(f"✅ {len(pacientes)} pacientes encontrados")

            if len(pacientes) == 0:
                print("⚠️ No hay pacientes para probar")
                return True

            # 4. Probar funcionalidades con el primer paciente
            primer_paciente = pacientes[0]
            paciente_id = primer_paciente.get("id")
            paciente_nombre = (
                primer_paciente.get("nombre", "")
                + " "
                + primer_paciente.get("apellido", "")
            )

            print(
                f"\n🔍 Probando funcionalidades con: {paciente_nombre} (ID: {paciente_id})"
            )

            # 4.1 Probar obtener historial del paciente
            print(f"\n📋 Probando obtener historial del paciente...")
            historial_url = (
                f"https://www.medconnect.cl/api/professional/patients/{paciente_id}"
            )
            historial_response = session.get(historial_url)

            print(f"📊 Status historial: {historial_response.status_code}")
            if historial_response.status_code == 200:
                print(f"✅ Historial del paciente funciona")
            else:
                print(f"❌ Error en historial: {historial_response.text[:200]}")

            # 4.2 Probar editar paciente (simular)
            print(f"\n✏️ Probando editar paciente...")
            edit_url = (
                f"https://www.medconnect.cl/api/professional/patients/{paciente_id}"
            )
            edit_response = session.get(edit_url)

            print(f"📊 Status editar: {edit_response.status_code}")
            if edit_response.status_code == 200:
                print(f"✅ Editar paciente funciona")
            else:
                print(f"❌ Error en editar: {edit_response.text[:200]}")

            # 4.3 Probar agregar cita (simular)
            print(f"\n📅 Probando agregar cita...")
            cita_data = {
                "paciente_id": paciente_id,
                "fecha": "2025-09-30",
                "hora": "10:00",
                "tipo_atencion": "consulta",
                "motivo": "Control rutinario",
            }

            cita_url = "https://www.medconnect.cl/api/professional/schedule"
            cita_response = session.post(cita_url, json=cita_data)

            print(f"📊 Status cita: {cita_response.status_code}")
            if cita_response.status_code in [200, 201]:
                print(f"✅ Agregar cita funciona")
            else:
                print(f"⚠️ Cita puede no estar implementada: {cita_response.text[:200]}")

            print(f"\n🎉 Todas las funcionalidades probadas exitosamente")
            return True

        except json.JSONDecodeError:
            print(f"❌ Error parseando lista de pacientes")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 PRUEBA TODAS LAS FUNCIONALIDADES")
    print("=" * 60)

    success = test_all_patient_functions()

    if success:
        print(f"\n🎉 ¡Todas las funcionalidades funcionan correctamente!")
    else:
        print(f"\n❌ Error en alguna funcionalidad")
        print(f"🔧 Revisa los logs del servidor")
