#!/usr/bin/env python3
"""
Script que simula el entorno de Railway para probar el registro
"""

import os
import sys
import requests
import json


def simulate_railway_test():
    """Simula el entorno de Railway para probar el registro"""

    print("🚀 Simulando entorno de Railway...")

    # Variables de Railway (las mismas del log)
    railway_vars = {
        "DATABASE_URL": "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@postgres.railway.internal:5432/railway",
        "PGHOST": "postgres.railway.internal",
        "PGDATABASE": "railway",
        "PGUSER": "postgres",
        "PGPASSWORD": "SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd",
        "PGPORT": "5432",
    }

    print("📋 Variables de Railway configuradas")

    # URL de la aplicación
    base_url = "https://www.medconnect.cl"

    print(f"🌐 Probando aplicación en: {base_url}")

    # 1. Probar endpoint de salud
    print("\n1️⃣ Probando endpoint de salud...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 2. Probar página de registro (GET)
    print("\n2️⃣ Probando página de registro (GET)...")
    try:
        response = requests.get(f"{base_url}/register", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Página de registro cargada correctamente")
        else:
            print(f"   ❌ Error: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 3. Probar registro de profesional
    print("\n3️⃣ Probando registro de profesional...")

    professional_data = {
        "email": "test_railway_prof@test.com",
        "password": "test123",
        "confirm_password": "test123",
        "nombre": "Test",
        "apellido": "Railway",
        "tipo_usuario": "profesional",
        "numero_registro": "RAIL123",
        "especialidad": "Medicina General",
        "profesion": "Médico",
        "anos_experiencia": "5",
        "institucion": "Hospital Railway",
        "direccion_consulta": "Calle Railway 123",
        "horario_atencion": "Lunes a Viernes 9-17",
        "idiomas": "Español, Inglés",
        "calificacion": "5.0",
    }

    try:
        response = requests.post(
            f"{base_url}/register", data=professional_data, timeout=30
        )
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            if "Usuario registrado exitosamente" in response.text:
                print("   ✅ Registro de profesional exitoso")
            elif "Error interno del servidor" in response.text:
                print("   ❌ Error interno del servidor")
                print(f"   Error completo: {response.text[:500]}...")
            else:
                print("   ⚠️ Respuesta inesperada")
                print(f"   Response: {response.text[:300]}...")
        else:
            print(f"   ❌ Status inesperado: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 4. Probar registro de paciente
    print("\n4️⃣ Probando registro de paciente...")

    patient_data = {
        "email": "test_railway_patient@test.com",
        "password": "test123",
        "confirm_password": "test123",
        "nombre": "Test",
        "apellido": "Patient",
        "tipo_usuario": "paciente",
        "rut": "12345678-9",
        "fecha_nacimiento": "1990-01-01",
        "genero": "Masculino",
        "telefono": "+56912345678",
        "direccion": "Calle Railway 456",
        "antecedentes_medicos": "Ninguno",
    }

    try:
        response = requests.post(f"{base_url}/register", data=patient_data, timeout=30)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            if "Usuario registrado exitosamente" in response.text:
                print("   ✅ Registro de paciente exitoso")
            elif "Error interno del servidor" in response.text:
                print("   ❌ Error interno del servidor")
                print(f"   Error completo: {response.text[:500]}...")
            else:
                print("   ⚠️ Respuesta inesperada")
                print(f"   Response: {response.text[:300]}...")
        else:
            print(f"   ❌ Status inesperado: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 5. Probar login con usuario registrado
    print("\n5️⃣ Probando login...")

    login_data = {"email": "test_railway_prof@test.com", "password": "test123"}

    try:
        response = requests.post(f"{base_url}/login", data=login_data, timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            if (
                "dashboard" in response.text.lower()
                or "paciente" in response.text.lower()
            ):
                print("   ✅ Login exitoso")
            else:
                print("   ⚠️ Login con respuesta inesperada")
                print(f"   Response: {response.text[:200]}...")
        else:
            print(f"   ❌ Login falló: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Error en login: {e}")

    print("\n🏁 Pruebas completadas")


if __name__ == "__main__":
    simulate_railway_test()
