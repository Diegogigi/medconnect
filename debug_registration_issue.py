#!/usr/bin/env python3
"""
Script para diagnosticar el problema de registro de usuarios
"""


def debug_registration_issue():
    """Diagnostica el problema de registro"""

    print("🔍 Diagnosticando problema de registro...")

    # 1. Verificar el endpoint /register
    print("\n1️⃣ Verificando endpoint /register...")

    # Leer app.py para verificar el endpoint
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            app_content = f.read()

        if '@app.route("/register", methods=["GET", "POST"])' in app_content:
            print("✅ Endpoint /register encontrado")
        else:
            print("❌ Endpoint /register NO encontrado")

        if "auth_manager.register_user" in app_content:
            print("✅ Llamada a auth_manager.register_user encontrada")
        else:
            print("❌ Llamada a auth_manager.register_user NO encontrada")

    except FileNotFoundError:
        print("❌ Archivo app.py no encontrado")

    # 2. Verificar auth_manager.py
    print("\n2️⃣ Verificando auth_manager.py...")

    try:
        with open("auth_manager.py", "r", encoding="utf-8") as f:
            auth_content = f.read()

        if "def register_user" in auth_content:
            print("✅ Método register_user encontrado en AuthManager")
        else:
            print("❌ Método register_user NO encontrado en AuthManager")

        if "self.postgres_db.register_user" in auth_content:
            print("✅ Llamada a postgres_db.register_user encontrada")
        else:
            print("❌ Llamada a postgres_db.register_user NO encontrada")

    except FileNotFoundError:
        print("❌ Archivo auth_manager.py no encontrado")

    # 3. Verificar postgresql_db_manager.py
    print("\n3️⃣ Verificando postgresql_db_manager.py...")

    try:
        with open("postgresql_db_manager.py", "r", encoding="utf-8") as f:
            postgres_content = f.read()

        if "def register_user" in postgres_content:
            print("✅ Método register_user encontrado en PostgreSQLDBManager")
        else:
            print("❌ Método register_user NO encontrado en PostgreSQLDBManager")

        if "def _register_patient" in postgres_content:
            print("✅ Método _register_patient encontrado")
        else:
            print("❌ Método _register_patient NO encontrado")

        if "def _register_professional" in postgres_content:
            print("✅ Método _register_professional encontrado")
        else:
            print("❌ Método _register_professional NO encontrado")

        if "self.conn.commit()" in postgres_content:
            print("✅ self.conn.commit() encontrado (correcto)")
        elif "self.connection.commit()" in postgres_content:
            print("❌ self.connection.commit() encontrado (INCORRECTO)")
        else:
            print("⚠️ No se encontró commit()")

    except FileNotFoundError:
        print("❌ Archivo postgresql_db_manager.py no encontrado")

    # 4. Crear script de prueba de registro
    print("\n4️⃣ Creando script de prueba de registro...")

    test_registration_script = '''#!/usr/bin/env python3
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
        print("\\n🔍 Probando registro de profesional...")
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
        print("\\n🔍 Probando registro de paciente...")
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
'''

    with open("test_registration.py", "w", encoding="utf-8") as f:
        f.write(test_registration_script)

    print("✅ Script de prueba creado: test_registration.py")

    print("\n5️⃣ Próximos pasos:")
    print("   1. Ejecutar: python test_registration.py")
    print("   2. Revisar los logs de Railway durante la prueba")
    print("   3. Verificar si hay errores específicos")


if __name__ == "__main__":
    debug_registration_issue()
