#!/usr/bin/env python3
"""
Script para probar el registro de usuarios
"""

import os
import sys
import requests
import json

def test_registration():
    """Prueba el registro de usuarios"""
    
    print("🧪 Probando registro de usuarios...")
    
    # URL de la aplicación
    base_url = "https://www.medconnect.cl"
    
    # Datos de prueba para profesional
    professional_data = {
        "email": "test_professional@test.com",
        "password": "test123",
        "confirm_password": "test123",
        "nombre": "Test",
        "apellido": "Professional",
        "tipo_usuario": "profesional",
        "numero_registro": "12345",
        "especialidad": "Medicina General",
        "profesion": "Médico",
        "anos_experiencia": "5",
        "institucion": "Hospital Test",
        "direccion_consulta": "Calle Test 123",
        "horario_atencion": "Lunes a Viernes 9-17",
        "idiomas": "Español, Inglés",
        "calificacion": "5.0"
    }
    
    # Datos de prueba para paciente
    patient_data = {
        "email": "test_patient@test.com",
        "password": "test123",
        "confirm_password": "test123",
        "nombre": "Test",
        "apellido": "Patient",
        "tipo_usuario": "paciente",
        "rut": "12345678-9",
        "fecha_nacimiento": "1990-01-01",
        "genero": "Masculino",
        "telefono": "+56912345678",
        "direccion": "Calle Test 456",
        "antecedentes_medicos": "Ninguno"
    }
    
    try:
        # Probar registro de profesional
        print("\n🔍 Probando registro de profesional...")
        response = requests.post(f"{base_url}/register", data=professional_data, timeout=30)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Registro de profesional exitoso")
        elif response.status_code == 500:
            print("❌ Error interno del servidor")
            print(f"   Error completo: {response.text}")
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
        
        # Probar registro de paciente
        print("\n🔍 Probando registro de paciente...")
        response = requests.post(f"{base_url}/register", data=patient_data, timeout=30)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Registro de paciente exitoso")
        elif response.status_code == 500:
            print("❌ Error interno del servidor")
            print(f"   Error completo: {response.text}")
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_registration()
