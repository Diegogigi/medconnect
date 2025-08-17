#!/usr/bin/env python3
"""
Script para verificar que la ruta de cambio de contraseñas esté registrada
"""

import requests
import time

def test_change_password_route():
    """Verificar que la ruta de cambio de contraseñas esté disponible"""
    print("🔍 Verificando ruta /api/profile/change-password...")
    
    # Esperar a que el servidor inicie
    for i in range(5):
        try:
            # Probar la ruta (debería dar 401 porque no estamos autenticados, no 404)
            response = requests.post('http://127.0.0.1:5000/api/profile/change-password', 
                                   json={'test': 'data'}, timeout=3)
            
            if response.status_code == 404:
                print("❌ ERROR: Ruta no encontrada (404)")
                print("🔄 Necesitas reiniciar el servidor:")
                print("   1. Presiona Ctrl+C en el servidor")
                print("   2. python app.py")
                return False
                
            elif response.status_code == 401:
                print("✅ Ruta encontrada (devuelve 401 - no autenticado)")
                print("🎉 ¡El cambio de contraseñas debería funcionar!")
                return True
                
            else:
                print(f"⚠️ Respuesta inesperada: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"⏳ Esperando servidor... intento {i+1}/5")
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("❌ No se pudo conectar al servidor")
    return False

if __name__ == "__main__":
    test_change_password_route() 