#!/usr/bin/env python3
"""
Script de prueba para verificar el endpoint de pacientes del profesional
"""

import requests
import json
import sys
import os

def test_patients_api():
    """Prueba el endpoint de pacientes del profesional"""
    
    # URL base (ajustar según tu configuración)
    base_url = "http://localhost:5000"
    
    print("🧪 Probando endpoint de pacientes del profesional...")
    
    # Test 1: Verificar que el endpoint responde
    print("📋 Test 1: Verificando respuesta del endpoint...")
    try:
        response = requests.get(f"{base_url}/api/professional/patients", timeout=10)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint responde correctamente")
            print(f"📊 Datos recibidos: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                pacientes = data.get('pacientes', [])
                print(f"👥 Pacientes encontrados: {len(pacientes)}")
                
                for i, paciente in enumerate(pacientes[:3]):  # Mostrar solo los primeros 3
                    print(f"  {i+1}. {paciente.get('nombre_completo', 'N/A')} - {paciente.get('rut', 'N/A')}")
                
                if len(pacientes) > 3:
                    print(f"  ... y {len(pacientes) - 3} más")
                    
            else:
                print("⚠️ Endpoint responde pero con error")
                print(f"📝 Mensaje: {data.get('message', 'Sin mensaje')}")
                
        elif response.status_code == 401:
            print("⚠️ Error 401: No autorizado (necesitas estar logueado)")
        elif response.status_code == 500:
            print("❌ Error 500: Error interno del servidor")
        else:
            print(f"⚠️ Status code inesperado: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: No se pudo conectar al servidor")
        print("💡 Asegúrate de que el servidor esté ejecutándose en http://localhost:5000")
    except requests.exceptions.Timeout:
        print("❌ Error de timeout: La solicitud tardó demasiado")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    # Test 2: Verificar estructura de respuesta
    print("\n📋 Test 2: Verificando estructura de respuesta...")
    try:
        response = requests.get(f"{base_url}/api/professional/patients", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Verificar campos requeridos
            required_fields = ['success', 'pacientes', 'total']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ Estructura de respuesta correcta")
                print(f"📊 Total de pacientes: {data.get('total', 0)}")
            else:
                print(f"⚠️ Campos faltantes: {missing_fields}")
                
            # Verificar estructura de pacientes si existen
            if data.get('pacientes'):
                paciente = data['pacientes'][0]
                paciente_fields = ['paciente_id', 'nombre_completo', 'rut', 'edad']
                missing_paciente_fields = [field for field in paciente_fields if field not in paciente]
                
                if not missing_paciente_fields:
                    print("✅ Estructura de paciente correcta")
                else:
                    print(f"⚠️ Campos faltantes en paciente: {missing_paciente_fields}")
                    
        else:
            print("⚠️ No se pudo verificar estructura (error en endpoint)")
            
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
    
    print("\n🎉 Pruebas completadas")

if __name__ == "__main__":
    test_patients_api() 