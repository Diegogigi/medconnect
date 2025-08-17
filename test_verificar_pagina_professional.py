#!/usr/bin/env python3
"""
Script para verificar qué está devolviendo la página professional
"""

import requests

def verificar_pagina_professional():
    """Verifica qué está devolviendo la página professional"""
    
    print("🔍 VERIFICACIÓN DE LA PÁGINA PROFESSIONAL")
    print("=" * 50)
    
    try:
        # Probar sin autenticación
        print("🔍 Probando sin autenticación...")
        response = requests.get("http://localhost:5000/professional", timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
        
        # Verificar si es HTML o JSON
        content = response.text[:500]
        print(f"   Primeros 500 caracteres:")
        print(f"   {content}")
        
        # Verificar si es página de login
        if 'login' in content.lower() or 'iniciar sesión' in content.lower():
            print("   ✅ Es página de login (esperado sin autenticación)")
        elif 'sugerenciasTratamiento' in content:
            print("   ✅ Es página professional (inesperado sin autenticación)")
        else:
            print("   ❓ Contenido no identificado")
        
        print()
        
        # Probar con autenticación
        print("🔍 Probando con autenticación...")
        session = requests.Session()
        
        # Login
        login_data = {
            'email': 'giselle.arratia@gmail.com',
            'password': 'Gigi2025'
        }
        
        login_response = session.post(
            "http://localhost:5000/login",
            data=login_data,
            timeout=10
        )
        
        print(f"   Login Status: {login_response.status_code}")
        
        # Obtener página professional autenticada
        prof_response = session.get("http://localhost:5000/professional", timeout=10)
        
        print(f"   Professional Status: {prof_response.status_code}")
        print(f"   Content-Type: {prof_response.headers.get('Content-Type', 'No especificado')}")
        
        # Verificar contenido
        content = prof_response.text[:1000]
        print(f"   Primeros 1000 caracteres:")
        print(f"   {content}")
        
        # Verificar elementos específicos
        elementos_buscar = [
            'sugerenciasTratamiento',
            'listaSugerenciasTratamiento',
            'sugerirTratamientoConIA',
            'realizarBusquedaPersonalizada',
            'obtenerTerminosSeleccionados'
        ]
        
        print("\n🔍 Verificando elementos específicos:")
        for elemento in elementos_buscar:
            if elemento in prof_response.text:
                print(f"   ✅ {elemento}")
            else:
                print(f"   ❌ {elemento}")
        
        # Verificar si es página de login
        if 'login' in prof_response.text.lower() or 'iniciar sesión' in prof_response.text.lower():
            print("\n❌ PROBLEMA: Aún devuelve página de login después de autenticación")
            return False
        elif 'sugerenciasTratamiento' in prof_response.text:
            print("\n✅ ÉXITO: Es la página professional correcta")
            return True
        else:
            print("\n❓ Contenido no identificado")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO VERIFICACIÓN DE PÁGINA PROFESSIONAL")
    print("=" * 60)
    
    resultado = verificar_pagina_professional()
    
    print(f"\n📊 RESULTADO: {'OK' if resultado else 'ERROR'}")
    
    if resultado:
        print("🎯 La página professional está funcionando correctamente")
    else:
        print("🎯 Hay un problema con la autenticación o la página professional") 