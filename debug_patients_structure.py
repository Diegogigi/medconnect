#!/usr/bin/env python3
"""
Script para debuggear la estructura de datos de pacientes
"""

import requests
import json


def debug_patients_structure():
    """Debuggear la estructura de datos de pacientes"""

    print("🔍 Debuggeando estructura de datos de pacientes...")
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

            if len(pacientes) > 0:
                primer_paciente = pacientes[0]
                print(f"\n📊 Estructura del primer paciente:")
                print(f"   ID: {primer_paciente.get('id', 'NO ENCONTRADO')}")
                print(f"   Nombre: {primer_paciente.get('nombre', 'NO ENCONTRADO')}")
                print(
                    f"   Apellido: {primer_paciente.get('apellido', 'NO ENCONTRADO')}"
                )
                print(f"   Email: {primer_paciente.get('email', 'NO ENCONTRADO')}")
                print(f"   Todos los campos disponibles:")
                for key, value in primer_paciente.items():
                    print(f"     - {key}: {value}")

                # Probar eliminación con el ID correcto
                paciente_id = primer_paciente.get("id")
                if paciente_id:
                    print(f"\n🗑️ Probando eliminación con ID: {paciente_id}")
                    delete_url = f"https://www.medconnect.cl/api/professional/patients/{paciente_id}"
                    delete_response = session.delete(
                        delete_url, headers={"X-Requested-With": "XMLHttpRequest"}
                    )

                    print(f"📊 Status: {delete_response.status_code}")
                    if delete_response.status_code == 200:
                        try:
                            data = delete_response.json()
                            print(
                                f"✅ Eliminación exitosa: {data.get('message', 'N/A')}"
                            )
                        except:
                            print(f"✅ Eliminación exitosa (sin JSON)")
                    else:
                        print(f"❌ Error en eliminación: {delete_response.text[:200]}")
                else:
                    print(f"❌ No se encontró ID del paciente")
            else:
                print("⚠️ No hay pacientes para debuggear")

        except json.JSONDecodeError:
            print(f"❌ Error parseando respuesta JSON")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 DEBUG ESTRUCTURA PACIENTES")
    print("=" * 60)

    debug_patients_structure()
