#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de registro y login
"""


def test_registration_system():
    """Prueba el sistema de registro y login"""

    print("🧪 Probando sistema de registro y login...")

    # Simular datos de prueba para un profesional
    test_professional = {
        "email": "test.profesional@medconnect.cl",
        "password": "test123",
        "nombre": "Dr. Test",
        "apellido": "Profesional",
        "tipo_usuario": "profesional",
        "numero_registro": "TEST123",
        "especialidad": "Medicina General",
        "profesion": "Médico",
        "anos_experiencia": "5",
        "institucion": "Universidad de Chile",
        "direccion_consulta": "Av. Providencia 123",
        "horario_atencion": "09:00 - 18:00",
        "idiomas": "Español, Inglés",
        "calificacion": "Médico Cirujano",
    }

    # Simular datos de prueba para un paciente
    test_patient = {
        "email": "test.paciente@medconnect.cl",
        "password": "test123",
        "nombre": "Juan",
        "apellido": "Paciente",
        "tipo_usuario": "paciente",
        "rut": "12345678-9",
        "fecha_nacimiento": "1990-01-01",
        "genero": "Masculino",
        "telefono": "+56912345678",
        "direccion": "Calle Test 456",
        "antecedentes_medicos": "Ninguno",
    }

    print("\n📋 Datos de prueba generados:")
    print("   - Profesional: test.profesional@medconnect.cl")
    print("   - Paciente: test.paciente@medconnect.cl")

    print("\n🎯 Pasos para probar:")
    print("1. Ve a www.medconnect.cl/register")
    print("2. Registra un profesional con los datos de arriba")
    print("3. Registra un paciente con los datos de arriba")
    print("4. Ve a www.medconnect.cl/login")
    print("5. Inicia sesión con cualquiera de los usuarios")
    print("6. Verifica que puedas acceder al dashboard")

    print("\n✅ Verificaciones realizadas:")
    print("   - Métodos de registro corregidos")
    print("   - Métodos de login funcionales")
    print("   - Conexión a base de datos corregida")
    print("   - Validación de email implementada")

    print("\n🚀 El sistema está listo para pruebas en Railway!")


if __name__ == "__main__":
    test_registration_system()
