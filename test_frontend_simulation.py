#!/usr/bin/env python3
"""
Script para simular exactamente el flujo del frontend
"""

import requests
import json
import time

def simular_flujo_frontend():
    """Simula exactamente el flujo del frontend"""
    
    print("🎭 SIMULACIÓN DEL FLUJO FRONTEND")
    print("=" * 50)
    
    session = requests.Session()
    
    try:
        # Paso 1: Login
        print("🔐 Paso 1: Login...")
        login_data = {
            'email': 'giselle.arratia@gmail.com',
            'password': 'Gigi2025'
        }
        
        login_response = session.post(
            "http://localhost:5000/login",
            data=login_data,
            timeout=10
        )
        
        if login_response.status_code not in [200, 302]:
            print(f"❌ Error en login: {login_response.status_code}")
            return False
        
        print("✅ Login exitoso")
        
        # Paso 2: Generar términos (como hace sugerirTratamientoConIA)
        print("\n🔍 Paso 2: Generando términos...")
        
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
        
        if terminos_response.status_code != 200:
            print(f"❌ Error generando términos: {terminos_response.status_code}")
            return False
        
        terminos_result = terminos_response.json()
        
        if not terminos_result.get('success'):
            print(f"❌ Error en términos: {terminos_result.get('message')}")
            return False
        
        print("✅ Términos generados")
        
        # Paso 3: Simular selección de términos (como hace obtenerTerminosSeleccionados)
        print("\n📋 Paso 3: Simulando selección de términos...")
        
        terminos_disponibles = terminos_result.get('terminos_disponibles', {})
        
        # Simular que el usuario selecciona los términos recomendados (que están marcados por defecto)
        terminos_seleccionados = []
        
        if terminos_disponibles.get('terminos_recomendados'):
            # Tomar los primeros 3 términos recomendados (que están marcados por defecto)
            terminos_seleccionados = terminos_disponibles['terminos_recomendados'][:3]
            print(f"   Términos recomendados seleccionados: {terminos_seleccionados}")
        
        if not terminos_seleccionados:
            # Si no hay recomendados, tomar de especialidad
            if terminos_disponibles.get('terminos_especialidad'):
                terminos_seleccionados = terminos_disponibles['terminos_especialidad'][:3]
                print(f"   Términos de especialidad seleccionados: {terminos_seleccionados}")
        
        if not terminos_seleccionados:
            print("❌ No se pudieron seleccionar términos")
            return False
        
        print(f"✅ Términos seleccionados: {terminos_seleccionados}")
        
        # Paso 4: Realizar búsqueda personalizada (como hace realizarBusquedaPersonalizada)
        print("\n🔍 Paso 4: Realizando búsqueda personalizada...")
        
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
                
                print("\n🎯 RESULTADO: Flujo frontend funcionando correctamente")
                return True
            else:
                print("   ⚠️ No se encontraron tratamientos")
                print("   Respuesta:", json.dumps(busqueda_result, indent=2)[:500])
                return True
        else:
            print(f"❌ Error en búsqueda: {busqueda_response.status_code}")
            print(f"   Respuesta: {busqueda_response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def verificar_elementos_html():
    """Verifica que los elementos HTML necesarios estén presentes"""
    
    print("\n🔍 VERIFICACIÓN DE ELEMENTOS HTML")
    print("=" * 40)
    
    try:
        # Obtener la página professional
        response = requests.get("http://localhost:5000/professional", timeout=10)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Verificar elementos necesarios
            elementos_requeridos = [
                'id="sugerenciasTratamiento"',
                'id="listaSugerenciasTratamiento"',
                'sugerirTratamientoConIA()',
                'realizarBusquedaPersonalizada(',
                'obtenerTerminosSeleccionados()'
            ]
            
            elementos_encontrados = []
            for elemento in elementos_requeridos:
                if elemento in html_content:
                    elementos_encontrados.append(elemento)
                    print(f"✅ {elemento}")
                else:
                    print(f"❌ {elemento}")
            
            print(f"\n📊 Elementos encontrados: {len(elementos_encontrados)}/{len(elementos_requeridos)}")
            
            if len(elementos_encontrados) == len(elementos_requeridos):
                print("✅ Todos los elementos HTML están presentes")
                return True
            else:
                print("❌ Faltan elementos HTML")
                return False
        else:
            print(f"❌ Error obteniendo página: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando HTML: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO SIMULACIÓN DEL FLUJO FRONTEND")
    print("=" * 60)
    
    # Verificar elementos HTML
    html_ok = verificar_elementos_html()
    
    # Simular flujo frontend
    flujo_ok = simular_flujo_frontend()
    
    print("\n📊 RESUMEN")
    print("=" * 20)
    print(f"✅ Elementos HTML: {'OK' if html_ok else 'ERROR'}")
    print(f"✅ Flujo frontend: {'OK' if flujo_ok else 'ERROR'}")
    
    if html_ok and flujo_ok:
        print("\n🎯 CONCLUSIÓN: El sistema está funcionando correctamente")
        print("   El problema puede estar en la interacción del usuario en el navegador")
    else:
        print("\n🎯 CONCLUSIÓN: Hay un problema en el sistema")
        print("   Se requiere más debugging") 