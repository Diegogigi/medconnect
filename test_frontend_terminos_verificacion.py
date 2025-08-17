#!/usr/bin/env python3
"""
Script para verificar que el frontend esté mostrando correctamente los términos de búsqueda
"""

import requests
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_frontend_terminos_display():
    """Prueba la visualización de términos en el frontend"""
    print("🔍 VERIFICACIÓN DE FRONTEND - TÉRMINOS DE BÚSQUEDA")
    print("=" * 60)
    
    # Verificar que el servidor esté corriendo
    try:
        health_response = requests.get("http://localhost:5000/", timeout=5)
        if health_response.status_code != 200:
            print("❌ El servidor no está corriendo en http://localhost:5000")
            print("   Por favor, inicia el servidor con: python app.py")
            return False
        print("✅ Servidor corriendo correctamente")
    except Exception as e:
        print("❌ No se puede conectar al servidor")
        print("   Por favor, inicia el servidor con: python app.py")
        return False
    
    # Verificar que la página professional.html esté disponible
    try:
        professional_response = requests.get("http://localhost:5000/professional", timeout=5)
        if professional_response.status_code != 200:
            print("❌ La página professional no está disponible")
            return False
        print("✅ Página professional disponible")
    except Exception as e:
        print(f"❌ Error accediendo a la página professional: {e}")
        return False
    
    # Verificar elementos HTML necesarios
    html_content = professional_response.text
    
    # Verificar contenedor de sugerencias
    if 'id="sugerenciasTratamiento"' in html_content:
        print("✅ Contenedor de sugerencias encontrado")
    else:
        print("❌ Contenedor de sugerencias NO encontrado")
        return False
    
    # Verificar contenedor de lista de sugerencias
    if 'id="listaSugerenciasTratamiento"' in html_content:
        print("✅ Contenedor de lista de sugerencias encontrado")
    else:
        print("❌ Contenedor de lista de sugerencias NO encontrado")
        return False
    
    # Verificar botón de sugerir tratamiento
    if 'sugerirTratamientoConIA()' in html_content:
        print("✅ Botón de sugerir tratamiento encontrado")
    else:
        print("❌ Botón de sugerir tratamiento NO encontrado")
        return False
    
    return True

def test_backend_endpoints():
    """Prueba los endpoints del backend para términos de búsqueda"""
    print("\n🔧 VERIFICACIÓN DE ENDPOINTS BACKEND")
    print("=" * 50)
    
    # Probar endpoint de generación de términos
    print("📋 Probando endpoint de generación de términos...")
    try:
        response = requests.post(
            "http://localhost:5000/api/copilot/generate-search-terms",
            json={
                'condicion': 'Dolor lumbar de 3 semanas',
                'especialidad': 'kinesiologia',
                'edad': 70
            },
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    terminos = data.get('terminos_disponibles', {})
                    print("✅ Endpoint de generación de términos funcionando")
                    print(f"📋 Términos básicos: {len(terminos.get('terminos_basicos', []))}")
                    print(f"🏥 Términos de especialidad: {len(terminos.get('terminos_especialidad', []))}")
                    print(f"👤 Términos por edad: {len(terminos.get('terminos_edad', []))}")
                    print(f"⭐ Términos recomendados: {len(terminos.get('terminos_recomendados', []))}")
                    return True
                else:
                    print(f"❌ Error en endpoint: {data.get('message', 'Error desconocido')}")
                    return False
            except json.JSONDecodeError:
                print("❌ Respuesta no es JSON válido")
                print(f"Respuesta: {response.text[:200]}...")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Respuesta: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_frontend_javascript():
    """Verifica que el JavaScript del frontend esté cargado correctamente"""
    print("\n🖥️ VERIFICACIÓN DE JAVASCRIPT FRONTEND")
    print("=" * 50)
    
    try:
        # Verificar que el archivo professional.js esté disponible
        js_response = requests.get("http://localhost:5000/static/js/professional.js", timeout=5)
        if js_response.status_code != 200:
            print("❌ Archivo professional.js no disponible")
            return False
        
        js_content = js_response.text
        
        # Verificar funciones necesarias
        funciones_requeridas = [
            'mostrarTerminosDisponibles',
            'realizarBusquedaPersonalizada',
            'realizarBusquedaAutomatica',
            'obtenerTerminosSeleccionados',
            'seleccionarTodosTerminos',
            'deseleccionarTodosTerminos'
        ]
        
        funciones_encontradas = []
        for funcion in funciones_requeridas:
            if funcion in js_content:
                funciones_encontradas.append(funcion)
                print(f"✅ Función {funcion} encontrada")
            else:
                print(f"❌ Función {funcion} NO encontrada")
        
        if len(funciones_encontradas) == len(funciones_requeridas):
            print("✅ Todas las funciones JavaScript están presentes")
            return True
        else:
            print(f"❌ Faltan {len(funciones_requeridas) - len(funciones_encontradas)} funciones")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando JavaScript: {e}")
        return False

def test_complete_flow():
    """Prueba el flujo completo de términos de búsqueda"""
    print("\n🔄 PRUEBA DE FLUJO COMPLETO")
    print("=" * 40)
    
    # Simular el flujo completo
    print("1️⃣ Generando términos disponibles...")
    try:
        terminos_response = requests.post(
            "http://localhost:5000/api/copilot/generate-search-terms",
            json={
                'condicion': 'Dificultad para tragar alimentos',
                'especialidad': 'fonoaudiologia',
                'edad': 8
            },
            timeout=10
        )
        
        if terminos_response.status_code == 200:
            terminos_data = terminos_response.json()
            if terminos_data.get('success'):
                terminos = terminos_data.get('terminos_disponibles', {})
                recomendados = terminos.get('terminos_recomendados', [])
                print(f"   ✅ {len(recomendados)} términos recomendados generados")
                
                # Simular selección de términos
                terminos_seleccionados = recomendados[:3] if len(recomendados) >= 3 else recomendados
                print(f"2️⃣ Simulando selección: {terminos_seleccionados}")
                
                # Probar búsqueda con términos seleccionados
                print("3️⃣ Probando búsqueda con términos seleccionados...")
                busqueda_response = requests.post(
                    "http://localhost:5000/api/copilot/search-with-terms",
                    json={
                        'condicion': 'Dificultad para tragar alimentos',
                        'especialidad': 'fonoaudiologia',
                        'edad': 8,
                        'terminos_seleccionados': terminos_seleccionados
                    },
                    timeout=10
                )
                
                if busqueda_response.status_code == 200:
                    busqueda_data = busqueda_response.json()
                    if busqueda_data.get('success'):
                        total_resultados = busqueda_data.get('total_resultados', 0)
                        print(f"   ✅ Búsqueda exitosa: {total_resultados} tratamientos encontrados")
                        print("   ✅ Flujo completo funcionando correctamente")
                        return True
                    else:
                        print(f"   ❌ Error en búsqueda: {busqueda_data.get('message')}")
                        return False
                else:
                    print(f"   ❌ Error HTTP en búsqueda: {busqueda_response.status_code}")
                    return False
            else:
                print(f"   ❌ Error generando términos: {terminos_data.get('message')}")
                return False
        else:
            print(f"   ❌ Error HTTP generando términos: {terminos_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en flujo completo: {e}")
        return False

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN COMPLETA DE FRONTEND - TÉRMINOS DE BÚSQUEDA")
    print("=" * 70)
    
    # Ejecutar todas las verificaciones
    resultados = []
    
    # Verificar frontend
    resultados.append(("Frontend HTML", test_frontend_terminos_display()))
    
    # Verificar endpoints backend
    resultados.append(("Endpoints Backend", test_backend_endpoints()))
    
    # Verificar JavaScript
    resultados.append(("JavaScript Frontend", test_frontend_javascript()))
    
    # Verificar flujo completo
    resultados.append(("Flujo Completo", test_complete_flow()))
    
    # Mostrar resumen
    print("\n📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 40)
    
    exitos = 0
    for nombre, resultado in resultados:
        if resultado:
            print(f"✅ {nombre}: OK")
            exitos += 1
        else:
            print(f"❌ {nombre}: FALLO")
    
    print(f"\n🎯 Resultado: {exitos}/{len(resultados)} verificaciones exitosas")
    
    if exitos == len(resultados):
        print("✅ TODAS LAS VERIFICACIONES EXITOSAS")
        print("✅ El frontend debería estar mostrando los términos correctamente")
        print("\n💡 Para probar manualmente:")
        print("   1. Ve a http://localhost:5000/professional")
        print("   2. Llena un diagnóstico (ej: 'Dolor lumbar')")
        print("   3. Haz clic en 'Sugerir Tratamiento con IA'")
        print("   4. Deberías ver los términos de búsqueda para seleccionar")
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("❌ Revisa los errores anteriores")

if __name__ == "__main__":
    main() 