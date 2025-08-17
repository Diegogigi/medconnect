#!/usr/bin/env python3
"""
Script para probar el mensaje de bienvenida
"""

import requests
import time

def test_welcome_message():
    """Probar el mensaje de bienvenida"""
    
    # URL base
    base_url = "http://localhost:5000"
    
    print("🧪 Probando mensaje de bienvenida...")
    
    try:
        # Intentar acceder a la página profesional
        print("📋 Accediendo a la página profesional...")
        response = requests.get(f"{base_url}/professional", timeout=10)
        
        if response.status_code == 200:
            print("✅ Página profesional cargada correctamente")
            
            # Verificar si el mensaje está en el HTML
            if 'welcome-toast' in response.text:
                print("✅ Elemento welcome-toast encontrado en el HTML")
            else:
                print("❌ Elemento welcome-toast NO encontrado en el HTML")
            
            # Verificar si el script está cargado
            if 'welcome-toast.js' in response.text:
                print("✅ Script welcome-toast.js cargado")
            else:
                print("❌ Script welcome-toast.js NO cargado")
                
            # Verificar si just_logged_in está presente
            if 'just_logged_in' in response.text:
                print("✅ Variable just_logged_in presente")
            else:
                print("❌ Variable just_logged_in NO presente")
                
        else:
            print(f"❌ Error al cargar la página: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. Asegúrate de que esté ejecutándose.")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_login_flow():
    """Probar el flujo de login completo"""
    
    base_url = "http://localhost:5000"
    
    print("\n🔐 Probando flujo de login...")
    
    try:
        # Simular login (esto requeriría credenciales reales)
        print("📝 Para probar el mensaje de bienvenida completo:")
        print("1. Ve a http://localhost:5000/login")
        print("2. Inicia sesión con credenciales válidas")
        print("3. Deberías ver el mensaje de bienvenida")
        print("4. Si no aparece, verifica la consola del navegador")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del mensaje de bienvenida...")
    test_welcome_message()
    test_login_flow()
    print("\n✅ Pruebas completadas") 