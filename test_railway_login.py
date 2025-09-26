#!/usr/bin/env python3
"""
Script para probar el login en la versión oficial de Railway
"""

import requests
import json

def test_railway_login():
    """Prueba el login en la versión oficial de Railway"""
    
    print("🧪 Probando login en Railway...")
    print("=" * 50)
    
    # URL de login
    login_url = "https://www.medconnect.cl/login"
    
    # Datos de prueba
    test_credentials = [
        {
            "email": "diego.castro.lagos@gmail.com",
            "password": "password123",
            "expected_type": "profesional"
        },
        {
            "email": "rodrigoandressilvabreve@gmail.com", 
            "password": "password123",
            "expected_type": "paciente"
        }
    ]
    
    for creds in test_credentials:
        print(f"\n🔐 Probando login con: {creds['email']}")
        
        try:
            # Crear sesión
            session = requests.Session()
            
            # Obtener página de login
            response = session.get(login_url)
            
            if response.status_code != 200:
                print(f"  ❌ Error obteniendo página de login: {response.status_code}")
                continue
            
            print(f"  ✅ Página de login cargada correctamente")
            
            # Intentar login
            login_data = {
                "email": creds["email"],
                "password": creds["password"]
            }
            
            login_response = session.post(login_url, data=login_data, allow_redirects=False)
            
            print(f"  📊 Status del login: {login_response.status_code}")
            
            if login_response.status_code == 302:
                redirect_url = login_response.headers.get('Location', '')
                print(f"  ✅ Login exitoso - Redirigiendo a: {redirect_url}")
                
                # Verificar redirección
                if "/professional" in redirect_url:
                    print(f"  ✅ Redirección correcta para profesional")
                elif "/patient" in redirect_url:
                    print(f"  ✅ Redirección correcta para paciente")
                else:
                    print(f"  ⚠️ Redirección inesperada: {redirect_url}")
                    
            elif login_response.status_code == 200:
                # Verificar si hay mensaje de error en el HTML
                if "Credenciales inválidas" in login_response.text:
                    print(f"  ❌ Login fallido - Credenciales inválidas")
                elif "Error" in login_response.text:
                    print(f"  ❌ Login fallido - Error en el sistema")
                else:
                    print(f"  ⚠️ Login no procesado correctamente")
            else:
                print(f"  ❌ Error inesperado: {login_response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error probando login: {e}")
    
    print("\n" + "=" * 50)
    print("📋 Resumen de pruebas:")
    print("1. Si todos los logins son exitosos: ✅ Sistema funcionando")
    print("2. Si hay errores de credenciales: ❌ Usuarios no existen en BD")
    print("3. Si hay errores 500: ❌ Problema de configuración")
    print("4. Si hay timeouts: ⏰ Aplicación no responde")

if __name__ == "__main__":
    test_railway_login()
