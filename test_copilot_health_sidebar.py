#!/usr/bin/env python3
"""
Script para probar la funcionalidad completa de Copilot Health en la sidebar
"""

import requests
import json
import time

def test_copilot_health_workflow():
    """Prueba el flujo completo de Copilot Health"""
    print("🤖 PRUEBA DE COPILOT HEALTH - SIDEBAR")
    print("=" * 50)
    
    # 1. Verificar que el servidor esté funcionando
    print("🔍 Verificando servidor...")
    try:
        response = requests.get("http://localhost:5000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Servidor funcionando")
        else:
            print(f"❌ Servidor respondió con código {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False
    
    # 2. Intentar login para obtener sesión
    print("\n🔐 Intentando login...")
    session = requests.Session()
    
    try:
        # Obtener página de login
        response = session.get("http://localhost:5000/login", timeout=10)
        if response.status_code != 200:
            print(f"❌ Error obteniendo página de login: {response.status_code}")
            return False
        
        # Intentar login
        login_data = {
            'username': 'admin@medconnect.cl',
            'password': 'admin123',
            'remember': 'on'
        }
        
        response = session.post("http://localhost:5000/login", data=login_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Login exitoso (o redirigido)")
        else:
            print(f"❌ Error en login: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error durante login: {e}")
        return False
    
    # 3. Probar el endpoint de generación de términos con sesión
    print("\n🔍 Probando generación de términos...")
    url = "http://localhost:5000/api/copilot/generate-search-terms"
    
    test_data = {
        "condicion": "Dolor lumbar crónico",
        "especialidad": "kinesiologia",
        "edad": 45
    }
    
    try:
        print(f"📤 Enviando datos: {test_data}")
        response = session.post(url, json=test_data, timeout=30)
        
        print(f"📥 Código de respuesta: {response.status_code}")
        print(f"📥 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    print("✅ Términos generados correctamente")
                    terminos = data.get('terminos_disponibles', {})
                    
                    # Mostrar estadísticas
                    total_terminos = 0
                    for categoria, lista in terminos.items():
                        if isinstance(lista, list):
                            total_terminos += len(lista)
                            print(f"   📋 {categoria}: {len(lista)} términos")
                    
                    print(f"   📊 Total: {total_terminos} términos")
                    
                    return True
                else:
                    print(f"❌ Error en respuesta: {data.get('message', 'Error desconocido')}")
                    return False
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
            
    except Exception as e:
        print(f"❌ Error en petición: {e}")
        return False

def test_search_with_terms():
    """Prueba la búsqueda con términos seleccionados"""
    print("\n🔍 Probando búsqueda con términos...")
    
    # Crear sesión autenticada
    session = requests.Session()
    
    try:
        # Obtener página de login
        response = session.get("http://localhost:5000/login", timeout=10)
        if response.status_code != 200:
            print(f"❌ Error obteniendo página de login: {response.status_code}")
            return False
        
        # Intentar login
        login_data = {
            'username': 'admin@medconnect.cl',
            'password': 'admin123',
            'remember': 'on'
        }
        
        response = session.post("http://localhost:5000/login", data=login_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Login exitoso para búsqueda")
        else:
            print(f"❌ Error en login: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error durante login: {e}")
        return False
    
    url = "http://localhost:5000/api/copilot/search-with-terms"
    
    test_data = {
        "condicion": "Dolor lumbar crónico",
        "especialidad": "kinesiologia",
        "edad": 45,
        "terminos_seleccionados": ["physical therapy", "rehabilitation", "exercise"]
    }
    
    try:
        response = session.post(url, json=test_data, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Búsqueda completada correctamente")
                planes = data.get('planes_tratamiento', [])
                print(f"   📄 Planes de tratamiento encontrados: {len(planes)}")
                
                if planes:
                    # Mostrar el primer plan como ejemplo
                    primer_plan = planes[0]
                    print(f"   📋 Ejemplo - Título: {primer_plan.get('titulo', 'Sin título')}")
                    print(f"   📋 Ejemplo - DOI: {primer_plan.get('doi', 'Sin DOI')}")
                
                return True
            else:
                print(f"❌ Error en búsqueda: {data.get('message', 'Error desconocido')}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Error: {error_data}")
            except:
                print(f"📄 Contenido: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        return False

def test_medical_apis_module():
    """Prueba el módulo de APIs médicas directamente"""
    print("\n🔍 Probando módulo de APIs médicas...")
    
    try:
        from medical_apis_integration import MedicalAPIsIntegration
        apis = MedicalAPIsIntegration()
        print("✅ Módulo importado correctamente")
        
        # Probar generación de términos
        print("🔍 Generando términos de búsqueda...")
        terminos = apis.generar_terminos_busqueda_disponibles(
            condicion="Dolor lumbar crónico",
            especialidad="kinesiologia",
            edad_paciente=45
        )
        
        if terminos:
            print("✅ Términos generados correctamente")
            total_terminos = 0
            for categoria, lista in terminos.items():
                if isinstance(lista, list):
                    total_terminos += len(lista)
            
            print(f"📊 Total de términos: {total_terminos}")
            return True
        else:
            print("❌ No se generaron términos")
            return False
            
    except Exception as e:
        print(f"❌ Error en módulo de APIs: {e}")
        import traceback
        print(f"📄 Traceback: {traceback.format_exc()}")
        return False

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE COPILOT HEALTH")
    print("=" * 50)
    
    # Prueba 1: Módulo de APIs médicas
    module_ok = test_medical_apis_module()
    
    if not module_ok:
        print("\n❌ Problema con el módulo de APIs médicas")
        return
    
    # Prueba 2: Generación de términos
    terms_ok = test_copilot_health_workflow()
    
    if not terms_ok:
        print("\n❌ Problema con la generación de términos")
        return
    
    # Prueba 3: Búsqueda con términos
    search_ok = test_search_with_terms()
    
    if not search_ok:
        print("\n❌ Problema con la búsqueda de términos")
        return
    
    print("\n✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
    print("🎉 Copilot Health está funcionando correctamente en la sidebar")
    print("\n💡 Para probar en el navegador:")
    print("   1. Inicia sesión en el navegador")
    print("   2. Ve a la página professional")
    print("   3. Completa el formulario de atención")
    print("   4. Haz clic en 'Activar Copilot Health' en la sidebar")
    print("   5. Observa el flujo completo en la sidebar")

if __name__ == "__main__":
    main() 