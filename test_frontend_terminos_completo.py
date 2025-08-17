#!/usr/bin/env python3
"""
Script para probar el flujo completo de términos con autenticación real
"""

import requests
import json
import time

def login_real():
    """Realiza login real con credenciales válidas"""
    print("🔐 Realizando login real...")
    
    session = requests.Session()
    
    # Datos de login reales
    login_data = {
        'email': 'giselle.arratia@gmail.com',
        'password': 'Gigi2025',
        'tipo_usuario': 'profesional'
    }
    
    try:
        # Realizar login
        response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 302:
            print("✅ Login exitoso - Redirect recibido")
            return session
        elif response.status_code == 200:
            # Verificar si el login fue exitoso
            if "dashboard" in response.text.lower() or "professional" in response.text.lower():
                print("✅ Login exitoso - Página de dashboard detectada")
                return session
            else:
                print("❌ Login falló - Página de login detectada")
                return None
        else:
            print(f"❌ Login falló - Status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return None

def test_terminos_con_auth():
    """Prueba la generación de términos con autenticación real"""
    print("\n🔍 PRUEBA DE TÉRMINOS CON AUTENTICACIÓN REAL")
    print("=" * 60)
    
    # Realizar login
    session = login_real()
    if not session:
        print("❌ No se pudo autenticar")
        return False
    
    # Probar endpoint de términos
    print("\n📋 Probando endpoint de términos...")
    try:
        response = session.post(
            "http://localhost:5000/api/copilot/generate-search-terms",
            json={
                'condicion': 'Dolor lumbar de 3 semanas',
                'especialidad': 'kinesiologia',
                'edad': 70
            },
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Respuesta JSON válida")
                
                if data.get('success'):
                    terminos = data.get('terminos_disponibles', {})
                    print("✅ Términos generados exitosamente")
                    
                    # Mostrar estructura de términos
                    print(f"\n📋 Estructura de términos:")
                    print(f"   - Términos básicos: {len(terminos.get('terminos_basicos', []))}")
                    print(f"   - Términos de especialidad: {len(terminos.get('terminos_especialidad', []))}")
                    print(f"   - Términos por edad: {len(terminos.get('terminos_edad', []))}")
                    print(f"   - Términos recomendados: {len(terminos.get('terminos_recomendados', []))}")
                    
                    # Mostrar algunos términos recomendados
                    recomendados = terminos.get('terminos_recomendados', [])
                    if recomendados:
                        print(f"\n⭐ Términos recomendados:")
                        for i, termino in enumerate(recomendados[:5], 1):
                            print(f"   {i}. {termino}")
                    
                    return True
                else:
                    print(f"❌ Error en respuesta: {data.get('message', 'Error desconocido')}")
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

def test_busqueda_con_terminos():
    """Prueba la búsqueda con términos seleccionados"""
    print("\n🔍 PRUEBA DE BÚSQUEDA CON TÉRMINOS")
    print("=" * 50)
    
    # Realizar login
    session = login_real()
    if not session:
        print("❌ No se pudo autenticar")
        return False
    
    # Primero generar términos
    print("1️⃣ Generando términos...")
    try:
        terminos_response = session.post(
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
                
                # Seleccionar algunos términos
                terminos_seleccionados = recomendados[:3] if len(recomendados) >= 3 else recomendados
                print(f"2️⃣ Términos seleccionados: {terminos_seleccionados}")
                
                # Probar búsqueda con términos seleccionados
                print("3️⃣ Probando búsqueda con términos...")
                busqueda_response = session.post(
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
                        planes = busqueda_data.get('planes_tratamiento', [])
                        print(f"   ✅ Búsqueda exitosa: {len(planes)} tratamientos encontrados")
                        
                        if planes:
                            print("   📄 Primeros tratamientos:")
                            for i, plan in enumerate(planes[:3], 1):
                                print(f"      {i}. {plan.get('titulo', 'Sin título')[:60]}...")
                        
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
        print(f"   ❌ Error en flujo: {e}")
        return False

def test_pagina_professional():
    """Verifica que la página professional esté accesible con autenticación"""
    print("\n🏗️ VERIFICACIÓN DE PÁGINA PROFESSIONAL")
    print("=" * 50)
    
    # Realizar login
    session = login_real()
    if not session:
        print("❌ No se pudo autenticar")
        return False
    
    try:
        response = session.get("http://localhost:5000/professional", timeout=10)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Verificar elementos críticos
            elementos_criticos = [
                'sugerenciasTratamiento',
                'listaSugerenciasTratamiento',
                'sugerirTratamientoConIA'
            ]
            
            elementos_encontrados = []
            for elemento in elementos_criticos:
                if elemento in html_content:
                    elementos_encontrados.append(elemento)
                    print(f"✅ {elemento} presente")
                else:
                    print(f"❌ {elemento} NO presente")
            
            # Verificar si es página de login
            if 'login' in html_content.lower():
                print("⚠️ PÁGINA DE LOGIN DETECTADA")
                print("💡 La autenticación no funcionó correctamente")
                return False
            else:
                print("✅ NO ES PÁGINA DE LOGIN")
                print(f"✅ {len(elementos_encontrados)}/{len(elementos_criticos)} elementos encontrados")
                return len(elementos_encontrados) == len(elementos_criticos)
                
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🔍 PRUEBA COMPLETA DE TÉRMINOS CON AUTENTICACIÓN")
    print("=" * 60)
    
    # Ejecutar todas las pruebas
    resultados = []
    
    # Verificar página professional
    resultados.append(("Página Professional", test_pagina_professional()))
    
    # Probar términos con auth
    resultados.append(("Términos con Auth", test_terminos_con_auth()))
    
    # Probar búsqueda con términos
    resultados.append(("Búsqueda con Términos", test_busqueda_con_terminos()))
    
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
        print("✅ El backend está funcionando correctamente")
        print("\n💡 Para probar en el frontend:")
        print("   1. Abre http://localhost:5000 en el navegador")
        print("   2. Inicia sesión como profesional")
        print("   3. Ve a la sección de atención")
        print("   4. Llena un diagnóstico")
        print("   5. Haz clic en 'Sugerir Tratamiento con IA'")
        print("   6. Abre la consola del navegador (F12) para ver los logs")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("❌ Revisa los errores anteriores")

if __name__ == "__main__":
    main() 