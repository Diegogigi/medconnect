#!/usr/bin/env python3
"""
Script para probar la eliminación final
"""

import requests
import json


def test_delete_final():
    """Probar la eliminación final"""

    print("🧪 Probando eliminación final...")
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
                print("⚠️ No hay pacientes para eliminar")
                return True

            # 4. Probar eliminación del primer paciente
            primer_paciente = pacientes[0]
            paciente_id = primer_paciente.get("id")
            paciente_nombre = (
                primer_paciente.get("nombre", "")
                + " "
                + primer_paciente.get("apellido", "")
            )

            print(
                f"🗑️ Intentando eliminar paciente: {paciente_nombre} (ID: {paciente_id})"
            )

            # Verificar que el ID no esté vacío
            if not paciente_id:
                print(f"❌ Error: ID del paciente está vacío")
                return False

            # Probar eliminación
            delete_url = (
                f"https://www.medconnect.cl/api/professional/patients/{paciente_id}"
            )
            delete_response = session.delete(
                delete_url,
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/json",
                },
            )

            print(f"📊 Status: {delete_response.status_code}")
            print(f"📄 URL: {delete_url}")
            print(f"📄 Response: {delete_response.text[:200]}")

            if delete_response.status_code == 200:
                try:
                    data = delete_response.json()
                    print(f"✅ Eliminación exitosa: {data.get('message', 'N/A')}")
                    return True
                except json.JSONDecodeError:
                    print(f"✅ Eliminación exitosa (sin JSON)")
                    return True
            else:
                print(f"❌ Error en eliminación: {delete_response.status_code}")
                return False

        except json.JSONDecodeError:
            print(f"❌ Error parseando lista de pacientes")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 PRUEBA ELIMINACIÓN FINAL")
    print("=" * 60)

    success = test_delete_final()

    if success:
        print(f"\n🎉 ¡Eliminación funciona correctamente!")
    else:
        print(f"\n❌ Error en la eliminación")
        print(f"🔧 Revisa los logs del servidor")
