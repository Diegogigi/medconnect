#!/usr/bin/env python3
"""
Script para probar la búsqueda personalizada con autenticación correcta
"""

import requests
import json
import time

def test_busqueda_personalizada_autenticada():
    """Prueba la búsqueda personalizada con autenticación"""
    
    print("🔍 PRUEBA DE BÚSQUEDA PERSONALIZADA CON AUTENTICACIÓN")
    print("=" * 60)
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        # Paso 1: Login
        print("🔐 Paso 1: Iniciando sesión...")
        
        login_data = {
            'email': 'giselle.arratia@gmail.com',
            'password': 'Gigi2025'
        }
        
        login_response = session.post(
            "http://localhost:5000/login",
            data=login_data,
            timeout=10
        )
        
        print(f"   Status Code: {login_response.status_code}")
        
        if login_response.status_code in [200, 302]:
            print("✅ Login exitoso")
            
            # Paso 2: Generar términos de búsqueda
            print("\n🔍 Paso 2: Generando términos de búsqueda...")
            
            terminos_data = {
                'condicion': 'Dolor lumbar de 3 semanas',
                'especialidad': 'kinesiologia',
                'edad': 70
            }
            
            terminos_response = session.post(
                "http://localhost:5000/api/copilot/generate-search-terms",
                json=terminos_data,
                timeout=15
            )
            
            print(f"   Status Code: {terminos_response.status_code}")
            
            if terminos_response.status_code == 200:
                terminos_result = terminos_response.json()
                print("✅ Términos generados exitosamente")
                
                if terminos_result.get('success'):
                    terminos_disponibles = terminos_result.get('terminos_disponibles', {})
                    
                    # Mostrar todos los términos disponibles
                    print("   📋 Términos disponibles:")
                    for categoria, terminos in terminos_disponibles.items():
                        if terminos:
                            print(f"   - {categoria}: {terminos[:3]}...")  # Mostrar solo los primeros 3
                    
                    # Usar términos recomendados o combinados
                    terminos_seleccionados = []
                    if terminos_disponibles.get('terminos_recomendados'):
                        terminos_seleccionados = terminos_disponibles['terminos_recomendados'][:3]
                    elif terminos_disponibles.get('terminos_combinados'):
                        terminos_seleccionados = terminos_disponibles['terminos_combinados'][:3]
                    elif terminos_disponibles.get('terminos_especialidad'):
                        terminos_seleccionados = terminos_disponibles['terminos_especialidad'][:3]
                    
                    if terminos_seleccionados:
                        print(f"   ✅ Términos seleccionados: {terminos_seleccionados}")
                        
                        # Paso 3: Realizar búsqueda personalizada
                        print("\n🔍 Paso 3: Realizando búsqueda personalizada...")
                        
                        busqueda_data = {
                            'condicion': 'Dolor lumbar de 3 semanas',
                            'especialidad': 'kinesiologia',
                            'edad': 70,
                            'terminos_seleccionados': terminos_seleccionados
                        }
                        
                        print(f"   📤 Enviando datos: {busqueda_data}")
                        
                        busqueda_response = session.post(
                            "http://localhost:5000/api/copilot/search-with-terms",
                            json=busqueda_data,
                            timeout=30
                        )
                        
                        print(f"   Status Code: {busqueda_response.status_code}")
                        
                        if busqueda_response.status_code == 200:
                            busqueda_result = busqueda_response.json()
                            print("✅ Búsqueda personalizada exitosa")
                            print(f"   Success: {busqueda_result.get('success')}")
                            print(f"   Total resultados: {busqueda_result.get('total_resultados', 0)}")
                            
                            if busqueda_result.get('planes_tratamiento'):
                                tratamientos = busqueda_result['planes_tratamiento']
                                print(f"   Tratamientos encontrados: {len(tratamientos)}")
                                
                                # Mostrar los primeros 3 tratamientos
                                for i, tratamiento in enumerate(tratamientos[:3], 1):
                                    titulo = tratamiento.get('titulo', 'Sin título')
                                    print(f"   {i}. {titulo[:80]}...")
                                
                                print("\n🎯 RESULTADO: Búsqueda personalizada funcionando correctamente")
                                return True
                            else:
                                print("   ⚠️ No se encontraron tratamientos")
                                print("   Respuesta completa:", json.dumps(busqueda_result, indent=2)[:500])
                                print("\n🎯 RESULTADO: Búsqueda personalizada funcionando pero sin resultados")
                                return True
                        else:
                            print(f"❌ Error en búsqueda personalizada: {busqueda_response.status_code}")
                            print(f"   Respuesta: {busqueda_response.text[:200]}")
                            return False
                    else:
                        print("⚠️ No se pudieron seleccionar términos")
                        print("   Términos disponibles:", terminos_disponibles)
                        return False
                else:
                    print(f"❌ Error generando términos: {terminos_result.get('message')}")
                    return False
            else:
                print(f"❌ Error en generación de términos: {terminos_response.status_code}")
                print(f"   Respuesta: {terminos_response.text[:200]}")
                return False
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"   Respuesta: {login_response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def test_busqueda_automatica_comparacion():
    """Prueba la búsqueda automática para comparar"""
    
    print("\n🔍 PRUEBA DE BÚSQUEDA AUTOMÁTICA (COMPARACIÓN)")
    print("=" * 50)
    
    session = requests.Session()
    
    try:
        # Login
        login_data = {
            'email': 'giselle.arratia@gmail.com',
            'password': 'Gigi2025'
        }
        
        session.post("http://localhost:5000/login", data=login_data, timeout=10)
        
        # Búsqueda automática
        busqueda_data = {
            'diagnostico': 'Dolor lumbar de 3 semanas',
            'especialidad': 'kinesiologia',
            'edad': 70
        }
        
        response = session.post(
            "http://localhost:5000/api/copilot/suggest-treatment",
            json=busqueda_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Búsqueda automática: {result.get('total_resultados', 0)} resultados")
            
            if result.get('planes_tratamiento'):
                tratamientos = result['planes_tratamiento']
                print(f"   Tratamientos encontrados: {len(tratamientos)}")
                for i, tratamiento in enumerate(tratamientos[:2], 1):
                    titulo = tratamiento.get('titulo', 'Sin título')
                    print(f"   {i}. {titulo[:60]}...")
            else:
                print("   ⚠️ No se encontraron tratamientos")
                print("   Respuesta:", json.dumps(result, indent=2)[:300])
            
            return True
        else:
            print(f"❌ Error en búsqueda automática: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE BÚSQUEDA PERSONALIZADA")
    print("=" * 60)
    
    # Probar búsqueda personalizada autenticada
    resultado_personalizada = test_busqueda_personalizada_autenticada()
    
    # Probar búsqueda automática para comparar
    resultado_automatica = test_busqueda_automatica_comparacion()
    
    print("\n📊 RESUMEN DE PRUEBAS")
    print("=" * 30)
    print(f"✅ Búsqueda personalizada: {'OK' if resultado_personalizada else 'ERROR'}")
    print(f"✅ Búsqueda automática: {'OK' if resultado_automatica else 'ERROR'}")
    
    if resultado_personalizada:
        print("\n🎯 CONCLUSIÓN: La búsqueda personalizada está funcionando correctamente")
        print("   El problema puede estar en el frontend o en la selección de términos")
    else:
        print("\n🎯 CONCLUSIÓN: Hay un problema con la búsqueda personalizada")
        print("   Se requiere más debugging") 