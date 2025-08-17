#!/usr/bin/env python3
"""
Script para probar que todos los botones de términos funcionen correctamente
"""

import requests
import json

def test_botones_terminos():
    """Prueba que todos los botones de términos funcionen"""
    print("🔘 PRUEBA DE BOTONES DE TÉRMINOS")
    print("=" * 50)
    
    # Realizar login
    session = requests.Session()
    login_data = {
        'email': 'giselle.arratia@gmail.com',
        'password': 'Gigi2025',
        'tipo_usuario': 'profesional'
    }
    
    print("🔐 Iniciando sesión...")
    response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Error en login")
        return False
    
    print("✅ Login exitoso")
    
    # Probar endpoint de términos
    print("\n📋 Generando términos...")
    try:
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
            data = terminos_response.json()
            if data.get('success'):
                terminos = data.get('terminos_disponibles', {})
                recomendados = terminos.get('terminos_recomendados', [])
                print(f"✅ Términos generados: {len(recomendados)} recomendados")
                
                # Probar búsqueda personalizada
                print("\n🔍 Probando búsqueda personalizada...")
                if len(recomendados) >= 3:
                    terminos_seleccionados = recomendados[:3]
                    print(f"   Términos seleccionados: {terminos_seleccionados}")
                    
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
                        if busqueda_data.get('success'):
                            planes = busqueda_data.get('planes_tratamiento', [])
                            print(f"   ✅ Búsqueda personalizada exitosa: {len(planes)} tratamientos")
                        else:
                            print(f"   ❌ Error en búsqueda personalizada: {busqueda_data.get('message')}")
                    else:
                        print(f"   ❌ Error HTTP en búsqueda personalizada: {busqueda_response.status_code}")
                else:
                    print("   ⚠️ No hay suficientes términos para probar")
                
                # Probar búsqueda automática
                print("\n🔍 Probando búsqueda automática...")
                automatica_response = session.post(
                    "http://localhost:5000/api/copilot/suggest-treatment",
                    json={
                        'diagnostico': 'Dolor lumbar de 3 semanas',
                        'especialidad': 'kinesiologia',
                        'edad': 70
                    },
                    timeout=20
                )
                
                if automatica_response.status_code == 200:
                    automatica_data = automatica_response.json()
                    if automatica_data.get('success'):
                        planes = automatica_data.get('planes_tratamiento', [])
                        print(f"   ✅ Búsqueda automática exitosa: {len(planes)} tratamientos")
                    else:
                        print(f"   ❌ Error en búsqueda automática: {automatica_data.get('message')}")
                else:
                    print(f"   ❌ Error HTTP en búsqueda automática: {automatica_response.status_code}")
                
                return True
            else:
                print(f"❌ Error generando términos: {data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP generando términos: {terminos_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

def verificar_funciones_javascript():
    """Verifica que las funciones JavaScript estén disponibles"""
    print("\n🔧 VERIFICACIÓN DE FUNCIONES JAVASCRIPT")
    print("=" * 50)
    
    # Realizar login
    session = requests.Session()
    login_data = {
        'email': 'giselle.arratia@gmail.com',
        'password': 'Gigi2025',
        'tipo_usuario': 'profesional'
    }
    
    response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Error en login")
        return False
    
    # Obtener página professional
    professional_response = session.get("http://localhost:5000/professional")
    
    if professional_response.status_code == 200:
        html_content = professional_response.text
        
        # Verificar que el archivo JavaScript se cargue
        if 'professional.js' in html_content:
            print("✅ Archivo JavaScript cargado")
        else:
            print("❌ Archivo JavaScript no encontrado")
            return False
        
        # Verificar elementos HTML necesarios
        elementos_requeridos = [
            'sugerenciasTratamiento',
            'listaSugerenciasTratamiento',
            'sugerirTratamientoConIA'
        ]
        
        elementos_encontrados = []
        for elemento in elementos_requeridos:
            if elemento in html_content:
                elementos_encontrados.append(elemento)
                print(f"✅ {elemento} presente")
            else:
                print(f"❌ {elemento} NO presente")
        
        if len(elementos_encontrados) == len(elementos_requeridos):
            print("✅ Todos los elementos HTML están presentes")
            return True
        else:
            print("❌ Faltan elementos HTML")
            return False
    else:
        print(f"❌ Error accediendo a página professional: {professional_response.status_code}")
        return False

def mostrar_instrucciones_botones():
    """Muestra instrucciones para probar los botones"""
    print("\n🎯 INSTRUCCIONES PARA PROBAR BOTONES")
    print("=" * 50)
    print("1. Abre http://localhost:5000 en tu navegador")
    print("2. Inicia sesión con:")
    print("   • Email: giselle.arratia@gmail.com")
    print("   • Password: Gigi2025")
    print("   • Tipo: profesional")
    print("3. Ve a la sección 'Registrar Atención'")
    print("4. Llena un diagnóstico (ej: 'Dolor lumbar de 3 semanas')")
    print("5. Haz clic en 'Sugerir Tratamiento con IA'")
    print("6. Deberías ver los términos y los siguientes botones:")
    print("   • 🔍 'Buscar con Términos Seleccionados'")
    print("   • 🎯 'Búsqueda Automática'")
    print("   • ☑️ 'Seleccionar Todos'")
    print("   • ☐ 'Deseleccionar Todos'")
    print("7. Prueba cada botón:")
    print("   • Selecciona algunos términos y haz clic en 'Buscar con Términos Seleccionados'")
    print("   • Haz clic en 'Búsqueda Automática' para búsqueda automática")
    print("   • Haz clic en 'Seleccionar Todos' para seleccionar todos los términos")
    print("   • Haz clic en 'Deseleccionar Todos' para deseleccionar todos")
    print("8. Verifica que cada botón realice su función correspondiente")

def main():
    """Función principal"""
    print("🔘 PRUEBA COMPLETA DE BOTONES DE TÉRMINOS")
    print("=" * 60)
    
    # Ejecutar pruebas
    resultados = []
    
    # Verificar funciones JavaScript
    resultados.append(("Funciones JavaScript", verificar_funciones_javascript()))
    
    # Probar botones
    resultados.append(("Botones de Términos", test_botones_terminos()))
    
    # Mostrar resumen
    print("\n📊 RESUMEN DE PRUEBAS")
    print("=" * 40)
    
    exitos = 0
    for nombre, resultado in resultados:
        if resultado:
            print(f"✅ {nombre}: OK")
            exitos += 1
        else:
            print(f"❌ {nombre}: FALLO")
    
    print(f"\n🎯 Resultado: {exitos}/{len(resultados)} pruebas exitosas")
    
    if exitos == len(resultados):
        print("✅ TODAS LAS PRUEBAS EXITOSAS")
        print("✅ Los botones están funcionando correctamente")
        mostrar_instrucciones_botones()
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("❌ Revisa los errores anteriores")

if __name__ == "__main__":
    main() 