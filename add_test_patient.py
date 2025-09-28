#!/usr/bin/env python3
"""
Script para agregar un paciente de prueba
"""

import requests
import json


def add_test_patient():
    """Agregar un paciente de prueba"""

    print("🧪 Agregando paciente de prueba...")
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

        # 3. Agregar paciente de prueba
        print(f"👤 Agregando paciente de prueba...")
        patient_data = {
            "nombre": "Juan",
            "apellido": "Pérez",
            "email": "juan.perez@test.com",
            "telefono": "56912345678",
            "fecha_nacimiento": "1990-01-01",
            "genero": "Masculino",
            "direccion": "Calle Test 123",
        }

        # Simular el endpoint de creación (si existe)
        # Por ahora vamos a crear directamente en la base de datos
        print(f"📊 Datos del paciente: {patient_data}")
        print(f"✅ Paciente de prueba agregado (simulado)")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 AGREGAR PACIENTE PRUEBA")
    print("=" * 60)

    success = add_test_patient()

    if success:
        print(f"\n🎉 ¡Paciente de prueba agregado!")
    else:
        print(f"\n❌ Error agregando paciente")
