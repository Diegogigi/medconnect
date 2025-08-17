#!/usr/bin/env python3
"""
Script para debuggear la búsqueda personalizada con términos seleccionados
"""

import requests
import json
import time

def test_busqueda_personalizada():
    """Prueba la búsqueda personalizada con términos seleccionados"""
    
    print("🔍 PRUEBA DE BÚSQUEDA PERSONALIZADA")
    print("=" * 50)
    
    # Datos de prueba
    test_data = {
        'condicion': 'Dolor lumbar de 3 semanas',
        'especialidad': 'kinesiologia',
        'edad': 70,
        'terminos_seleccionados': ['low back pain', 'physical therapy', 'exercise']
    }
    
    print(f"📋 Datos de prueba:")
    print(f"   Condición: {test_data['condicion']}")
    print(f"   Especialidad: {test_data['especialidad']}")
    print(f"   Edad: {test_data['edad']}")
    print(f"   Términos seleccionados: {test_data['terminos_seleccionados']}")
    print()
    
    # Probar endpoint de búsqueda personalizada
    try:
        print("🔍 Probando endpoint /api/copilot/search-with-terms...")
        
        response = requests.post(
            "http://localhost:5000/api/copilot/search-with-terms",
            json=test_data,
            timeout=30
        )
        
        print(f"📊 Respuesta HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta exitosa")
            print(f"   Success: {data.get('success')}")
            print(f"   Total resultados: {data.get('total_resultados', 0)}")
            
            if data.get('planes_tratamiento'):
                print(f"   Tratamientos encontrados: {len(data['planes_tratamiento'])}")
                for i, tratamiento in enumerate(data['planes_tratamiento'][:3], 1):
                    print(f"   {i}. {tratamiento.get('titulo', 'Sin título')}")
            else:
                print("   ⚠️ No se encontraron tratamientos")
                
        elif response.status_code == 401:
            print("❌ Error de autenticación - necesita login")
        elif response.status_code == 429:
            print("⚠️ Rate limiting detectado")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - servidor no disponible")
    except requests.exceptions.Timeout:
        print("❌ Timeout - la operación tardó demasiado")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_backend_directo():
    """Prueba el backend directamente sin Flask"""
    
    print("\n🔍 PRUEBA DIRECTA DEL BACKEND")
    print("=" * 50)
    
    try:
        from medical_apis_integration import MedicalAPIsIntegration
        
        apis = MedicalAPIsIntegration()
        
        # Datos de prueba
        condicion = 'Dolor lumbar de 3 semanas'
        especialidad = 'kinesiologia'
        edad_paciente = 70
        terminos_seleccionados = ['low back pain', 'physical therapy', 'exercise']
        
        print(f"📋 Datos de prueba:")
        print(f"   Condición: {condicion}")
        print(f"   Especialidad: {especialidad}")
        print(f"   Edad: {edad_paciente}")
        print(f"   Términos seleccionados: {terminos_seleccionados}")
        print()
        
        # Probar función directamente
        print("🔍 Probando buscar_con_terminos_personalizados...")
        
        resultados = apis.buscar_con_terminos_personalizados(
            condicion=condicion,
            especialidad=especialidad,
            terminos_seleccionados=terminos_seleccionados,
            edad_paciente=edad_paciente
        )
        
        print("✅ Función ejecutada exitosamente")
        print(f"   Tratamientos PubMed: {len(resultados.get('tratamientos_pubmed', []))}")
        print(f"   Tratamientos Europe PMC: {len(resultados.get('tratamientos_europepmc', []))}")
        print(f"   Preguntas científicas: {len(resultados.get('preguntas_cientificas', []))}")
        
        total_tratamientos = len(resultados.get('tratamientos_pubmed', [])) + len(resultados.get('tratamientos_europepmc', []))
        print(f"   Total tratamientos: {total_tratamientos}")
        
        if total_tratamientos > 0:
            print("✅ Búsqueda personalizada funcionando correctamente")
        else:
            print("⚠️ No se encontraron tratamientos")
            
    except Exception as e:
        print(f"❌ Error en prueba directa: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

def test_frontend_flow():
    """Prueba el flujo completo del frontend"""
    
    print("\n🔍 PRUEBA DEL FLUJO FRONTEND")
    print("=" * 50)
    
    # Simular login
    session = requests.Session()
    
    try:
        print("🔐 Intentando login...")
        
        login_data = {
            'email': 'giselle.arratia@gmail.com',
            'password': 'Gigi2025'
        }
        
        login_response = session.post(
            "http://localhost:5000/login",
            data=login_data,
            timeout=10
        )
        
        if login_response.status_code in [200, 302]:
            print("✅ Login exitoso")
            
            # Probar generación de términos
            print("🔍 Probando generación de términos...")
            
            terminos_response = session.post(
                "http://localhost:5000/api/copilot/generate-search-terms",
                json={
                    'condicion': 'Dolor lumbar de 3 semanas',
                    'especialidad': 'kinesiologia',
                    'edad': 70
                },
                timeout=15
            )
            
            if terminos_response.status_code == 200:
                terminos_data = terminos_response.json()
                print("✅ Términos generados exitosamente")
                
                if terminos_data.get('success'):
                    terminos_disponibles = terminos_data.get('terminos_disponibles', {})
                    recomendados = terminos_disponibles.get('recomendados', [])
                    
                    if recomendados:
                        terminos_seleccionados = recomendados[:3]  # Tomar los primeros 3
                        print(f"   Términos seleccionados: {terminos_seleccionados}")
                        
                        # Probar búsqueda personalizada
                        print("🔍 Probando búsqueda personalizada...")
                        
                        busqueda_response = session.post(
                            "http://localhost:5000/api/copilot/search-with-terms",
                            json={
                                'condicion': 'Dolor lumbar de 3 semanas',
                                'especialidad': 'kinesiologia',
                                'edad': 70,
                                'terminos_seleccionados': terminos_seleccionados
                            },
                            timeout=20
                        )
                        
                        if busqueda_response.status_code == 200:
                            busqueda_data = busqueda_response.json()
                            print("✅ Búsqueda personalizada exitosa")
                            print(f"   Total resultados: {busqueda_data.get('total_resultados', 0)}")
                            
                            if busqueda_data.get('planes_tratamiento'):
                                print(f"   Tratamientos encontrados: {len(busqueda_data['planes_tratamiento'])}")
                            else:
                                print("   ⚠️ No se encontraron tratamientos")
                        else:
                            print(f"❌ Error en búsqueda personalizada: {busqueda_response.status_code}")
                            print(f"   Respuesta: {busqueda_response.text[:200]}")
                    else:
                        print("⚠️ No se generaron términos recomendados")
                else:
                    print(f"❌ Error generando términos: {terminos_data.get('message')}")
            else:
                print(f"❌ Error en generación de términos: {terminos_response.status_code}")
                
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en prueba de flujo: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE BÚSQUEDA PERSONALIZADA")
    print("=" * 60)
    
    # Probar endpoint Flask
    test_busqueda_personalizada()
    
    # Probar backend directamente
    test_backend_directo()
    
    # Probar flujo completo
    test_frontend_flow()
    
    print("\n✅ PRUEBAS COMPLETADAS") 