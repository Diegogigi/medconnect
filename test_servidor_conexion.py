#!/usr/bin/env python3
"""
Script para probar la conexión del servidor y diagnosticar errores
"""

import requests
import json
import time

def test_server_health():
    """Prueba la salud del servidor"""
    print("🔍 Probando salud del servidor...")
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
            return True
        else:
            print(f"⚠️ Servidor respondió con código {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor")
        return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False

def login_and_get_session():
    """Inicia sesión y obtiene cookies de sesión"""
    print("\n🔐 Iniciando sesión...")
    
    session = requests.Session()
    
    # Primero obtener la página de login para obtener el token CSRF
    try:
        response = session.get("http://localhost:5000/login", timeout=10)
        if response.status_code != 200:
            print(f"❌ Error obteniendo página de login: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error conectando a login: {e}")
        return None
    
    # Datos de login (usar credenciales de prueba)
    login_data = {
        'username': 'admin@medconnect.cl',
        'password': 'admin123',
        'remember': 'on'
    }
    
    try:
        response = session.post("http://localhost:5000/login", data=login_data, timeout=10)
        
        if response.status_code == 200:
            # Verificar si el login fue exitoso
            if 'dashboard' in response.url or 'professional' in response.url:
                print("✅ Login exitoso")
                return session
            else:
                print("❌ Login falló - redirigido a login")
                return None
        else:
            print(f"❌ Error en login: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error durante login: {e}")
        return None

def test_search_endpoint_with_auth():
    """Prueba el endpoint de búsqueda con autenticación"""
    print("\n🔍 Probando endpoint de búsqueda con autenticación...")
    
    # Obtener sesión autenticada
    session = login_and_get_session()
    if not session:
        print("❌ No se pudo obtener sesión autenticada")
        return False
    
    url = "http://localhost:5000/api/copilot/search-with-terms"
    
    # Datos de prueba
    test_data = {
        "condicion": "Dolor lumbar",
        "especialidad": "kinesiologia",
        "edad": 30,
        "terminos_seleccionados": ["physical therapy", "rehabilitation"]
    }
    
    try:
        print(f"📤 Enviando datos: {test_data}")
        response = session.post(url, json=test_data, timeout=30)
        
        print(f"📥 Código de respuesta: {response.status_code}")
        print(f"📥 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Respuesta JSON válida")
                print(f"📊 Total resultados: {data.get('total_resultados', 0)}")
                print(f"📄 Planes de tratamiento: {len(data.get('planes_tratamiento', []))}")
                return True
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"📄 Contenido de respuesta: {response.text[:500]}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Error: {error_data}")
            except:
                print(f"📄 Contenido: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout en la petición")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_search_endpoint():
    """Prueba el endpoint de búsqueda sin autenticación (para comparar)"""
    print("\n🔍 Probando endpoint de búsqueda sin autenticación...")
    
    url = "http://localhost:5000/api/copilot/search-with-terms"
    
    # Datos de prueba
    test_data = {
        "condicion": "Dolor lumbar",
        "especialidad": "kinesiologia",
        "edad": 30,
        "terminos_seleccionados": ["physical therapy", "rehabilitation"]
    }
    
    try:
        print(f"📤 Enviando datos: {test_data}")
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"📥 Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Respuesta JSON válida")
                return True
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"📄 Contenido de respuesta: {response.text[:200]}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_medical_apis_module():
    """Prueba la importación del módulo de APIs médicas"""
    print("\n🔍 Probando módulo de APIs médicas...")
    
    try:
        from medical_apis_integration import MedicalAPIsIntegration
        print("✅ Módulo importado correctamente")
        
        # Crear instancia
        apis = MedicalAPIsIntegration()
        print("✅ Instancia creada correctamente")
        
        # Probar búsqueda simple
        print("🔍 Probando búsqueda simple...")
        resultados = apis.buscar_con_terminos_personalizados(
            condicion="Dolor lumbar",
            especialidad="kinesiologia",
            terminos_seleccionados=["physical therapy"],
            edad_paciente=30
        )
        
        print(f"✅ Búsqueda completada")
        print(f"📊 PubMed: {len(resultados.get('tratamientos_pubmed', []))}")
        print(f"📊 Europe PMC: {len(resultados.get('tratamientos_europepmc', []))}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando módulo: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en el módulo: {e}")
        import traceback
        print(f"📄 Traceback: {traceback.format_exc()}")
        return False

def main():
    """Función principal"""
    print("🤖 DIAGNÓSTICO DE CONEXIÓN DEL SERVIDOR")
    print("=" * 50)
    
    # Prueba 1: Salud del servidor
    server_ok = test_server_health()
    
    if not server_ok:
        print("\n❌ El servidor no está funcionando correctamente")
        print("💡 Verifica que el servidor esté ejecutándose con: python app.py")
        return
    
    # Prueba 2: Módulo de APIs médicas
    module_ok = test_medical_apis_module()
    
    if not module_ok:
        print("\n❌ Problema con el módulo de APIs médicas")
        return
    
    # Prueba 3: Endpoint sin autenticación (para comparar)
    test_search_endpoint()
    
    # Prueba 4: Endpoint con autenticación
    endpoint_ok = test_search_endpoint_with_auth()
    
    if endpoint_ok:
        print("\n✅ Todas las pruebas pasaron correctamente")
        print("🎉 El sistema está funcionando correctamente")
    else:
        print("\n❌ Problema con el endpoint de búsqueda")
        print("💡 El problema es de autenticación - el endpoint requiere login")

if __name__ == "__main__":
    main() 