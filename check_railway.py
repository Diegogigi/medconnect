#!/usr/bin/env python3
"""
Script para verificar configuración en Railway
"""

import os
import requests
import json

def check_railway_deployment():
    """Verifica el estado del deployment en Railway"""
    
    print("🚀 Verificando deployment en Railway...")
    
    try:
        # Intentar hacer una petición a la aplicación
        response = requests.get('https://www.medconnect.cl/health', timeout=10)
        
        if response.status_code == 200:
            print("✅ Aplicación respondiendo correctamente")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"⚠️ Aplicación respondiendo con status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando a la aplicación: {e}")
    
    print("\n📋 Para verificar Railway:")
    print("1. Ve a https://railway.app/dashboard")
    print("2. Selecciona tu proyecto MedConnect")
    print("3. Ve a la pestaña 'Variables'")
    print("4. Verifica que DATABASE_URL esté configurada")
    print("5. Ve a la pestaña 'Deployments'")
    print("6. Revisa los logs del último deployment")

if __name__ == "__main__":
    check_railway_deployment()
