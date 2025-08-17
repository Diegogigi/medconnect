#!/usr/bin/env python3
"""
Script para probar la funcionalidad de términos de búsqueda en el frontend
"""

import requests
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_generate_search_terms():
    """Prueba la generación de términos de búsqueda"""
    print("🔍 PRUEBA DE GENERACIÓN DE TÉRMINOS DE BÚSQUEDA")
    print("=" * 60)
    
    url = "http://localhost:5000/api/copilot/generate-search-terms"
    data = {
        'condicion': 'Dolor lumbar de 3 semanas',
        'especialidad': 'kinesiologia',
        'edad': 70
    }
    
    try:
        print("🔍 Enviando solicitud de términos...")
        response = requests.post(url, json=data, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('success'):
                    terminos = result.get('terminos_disponibles', {})
                    print("✅ Términos generados exitosamente")
                    print(f"📋 Términos básicos: {len(terminos.get('terminos_basicos', []))}")
                    print(f"🏥 Términos de especialidad: {len(terminos.get('terminos_especialidad', []))}")
                    print(f"👤 Términos por edad: {len(terminos.get('terminos_edad', []))}")
                    print(f"⭐ Términos recomendados: {len(terminos.get('terminos_recomendados', []))}")
                    
                    # Mostrar algunos términos recomendados
                    recomendados = terminos.get('terminos_recomendados', [])
                    if recomendados:
                        print("\n⭐ Términos recomendados:")
                        for i, termino in enumerate(recomendados[:5], 1):
                            print(f"   {i}. {termino}")
                else:
                    print(f"❌ Error: {result.get('message', 'Error desconocido')}")
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"Respuesta: {response.text[:200]}...")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Respuesta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_search_with_terms():
    """Prueba la búsqueda con términos seleccionados"""
    print("\n👨‍⚕️ PRUEBA DE BÚSQUEDA CON TÉRMINOS SELECCIONADOS")
    print("=" * 60)
    
    url = "http://localhost:5000/api/copilot/search-with-terms"
    data = {
        'condicion': 'Dolor lumbar de 3 semanas',
        'especialidad': 'kinesiologia',
        'edad': 70,
        'terminos_seleccionados': [
            'geriatric rehabilitation',
            'elderly physical therapy',
            'back pain',
            'rehabilitation'
        ]
    }
    
    try:
        print("🔍 Enviando búsqueda con términos personalizados...")
        response = requests.post(url, json=data, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('success'):
                    planes = result.get('planes_tratamiento', [])
                    total = result.get('total_resultados', 0)
                    print("✅ Búsqueda personalizada exitosa")
                    print(f"📄 Total tratamientos encontrados: {total}")
                    
                    if planes:
                        print("\n📄 Primeros tratamientos:")
                        for i, plan in enumerate(planes[:3], 1):
                            print(f"   {i}. {plan.get('titulo', 'Sin título')[:80]}...")
                            print(f"      DOI: {plan.get('doi', 'Sin DOI')}")
                            print(f"      Fuente: {plan.get('fuente', 'Sin fuente')}")
                            print()
                else:
                    print(f"❌ Error: {result.get('message', 'Error desconocido')}")
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"Respuesta: {response.text[:200]}...")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Respuesta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_comparison_automatic_vs_personalized():
    """Compara búsqueda automática vs personalizada"""
    print("\n🔄 COMPARACIÓN DE BÚSQUEDAS")
    print("=" * 50)
    
    # Búsqueda automática
    print("\n📊 BÚSQUEDA AUTOMÁTICA:")
    auto_url = "http://localhost:5000/api/copilot/suggest-treatment"
    auto_data = {
        'diagnostico': 'Dolor lumbar de 3 semanas',
        'especialidad': 'kinesiologia',
        'edad': 70
    }
    
    try:
        response = requests.post(auto_url, json=auto_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                planes_auto = result.get('planes_tratamiento', [])
                print(f"   Total resultados automáticos: {len(planes_auto)}")
            else:
                print(f"   Error automático: {result.get('message')}")
        else:
            print(f"   Error HTTP {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Búsqueda personalizada
    print("\n📊 BÚSQUEDA PERSONALIZADA:")
    personal_url = "http://localhost:5000/api/copilot/search-with-terms"
    personal_data = {
        'condicion': 'Dolor lumbar de 3 semanas',
        'especialidad': 'kinesiologia',
        'edad': 70,
        'terminos_seleccionados': ['geriatric rehabilitation', 'elderly physical therapy']
    }
    
    try:
        response = requests.post(personal_url, json=personal_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                planes_personal = result.get('planes_tratamiento', [])
                print(f"   Total resultados personalizados: {len(planes_personal)}")
                print(f"   Términos seleccionados: {personal_data['terminos_seleccionados']}")
            else:
                print(f"   Error personalizado: {result.get('message')}")
        else:
            print(f"   Error HTTP {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")

def test_frontend_integration():
    """Simula la integración completa del frontend"""
    print("\n🖥️ SIMULACIÓN DE INTEGRACIÓN FRONTEND")
    print("=" * 50)
    
    # Paso 1: Generar términos
    print("1️⃣ Generando términos disponibles...")
    terminos_response = requests.post(
        "http://localhost:5000/api/copilot/generate-search-terms",
        json={
            'condicion': 'Dificultad para tragar alimentos',
            'especialidad': 'fonoaudiologia',
            'edad': 8
        },
        timeout=30
    )
    
    if terminos_response.status_code == 200:
        terminos_data = terminos_response.json()
        if terminos_data.get('success'):
            terminos = terminos_data.get('terminos_disponibles', {})
            recomendados = terminos.get('terminos_recomendados', [])
            print(f"   ✅ {len(recomendados)} términos recomendados generados")
            
            # Paso 2: Simular selección del profesional
            print("2️⃣ Simulando selección del profesional...")
            terminos_seleccionados = recomendados[:3]  # Seleccionar los primeros 3
            print(f"   👨‍⚕️ Términos seleccionados: {terminos_seleccionados}")
            
            # Paso 3: Realizar búsqueda personalizada
            print("3️⃣ Realizando búsqueda personalizada...")
            busqueda_response = requests.post(
                "http://localhost:5000/api/copilot/search-with-terms",
                json={
                    'condicion': 'Dificultad para tragar alimentos',
                    'especialidad': 'fonoaudiologia',
                    'edad': 8,
                    'terminos_seleccionados': terminos_seleccionados
                },
                timeout=30
            )
            
            if busqueda_response.status_code == 200:
                busqueda_data = busqueda_response.json()
                if busqueda_data.get('success'):
                    total_resultados = busqueda_data.get('total_resultados', 0)
                    print(f"   ✅ Búsqueda completada: {total_resultados} tratamientos encontrados")
                    print("   ✅ Integración frontend-backend funcionando correctamente")
                else:
                    print(f"   ❌ Error en búsqueda: {busqueda_data.get('message')}")
            else:
                print(f"   ❌ Error HTTP en búsqueda: {busqueda_response.status_code}")
        else:
            print(f"   ❌ Error generando términos: {terminos_data.get('message')}")
    else:
        print(f"   ❌ Error HTTP generando términos: {terminos_response.status_code}")

def main():
    """Función principal"""
    print("🔍 PRUEBAS DE TÉRMINOS DE BÚSQUEDA EN FRONTEND")
    print("=" * 60)
    
    # Verificar que el servidor esté corriendo
    try:
        health_response = requests.get("http://localhost:5000/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ El servidor no está corriendo en http://localhost:5000")
            print("   Por favor, inicia el servidor con: python app.py")
            return
        print("✅ Servidor corriendo correctamente")
    except Exception as e:
        print("❌ No se puede conectar al servidor")
        print("   Por favor, inicia el servidor con: python app.py")
        return
    
    # Ejecutar pruebas
    test_generate_search_terms()
    test_search_with_terms()
    test_comparison_automatic_vs_personalized()
    test_frontend_integration()
    
    print("\n✅ Todas las pruebas completadas")

if __name__ == "__main__":
    main() 