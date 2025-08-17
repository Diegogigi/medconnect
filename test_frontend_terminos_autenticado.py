#!/usr/bin/env python3
"""
Script para verificar el frontend con autenticación simulada
"""

import requests
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def login_and_get_session():
    """Realiza login y obtiene la sesión"""
    print("🔐 Realizando login...")
    
    session = requests.Session()
    
    # Datos de login
    login_data = {
        'email': 'giselle.arratia@gmail.com',
        'password': '123456',
        'tipo_usuario': 'profesional'
    }
    
    try:
        # Realizar login
        response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 302:  # Redirect después del login exitoso
            print("✅ Login exitoso - Redirect recibido")
            return session
        elif response.status_code == 200:
            print("⚠️ Login devolvió 200 - Verificando contenido...")
            if "dashboard" in response.text.lower() or "professional" in response.text.lower():
                print("✅ Login exitoso - Página de dashboard detectada")
                return session
            else:
                print("❌ Login falló - Página de login detectada")
                print(f"Contenido: {response.text[:200]}...")
                return None
        else:
            print(f"❌ Login falló - Status: {response.status_code}")
            print(f"Respuesta: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return None

def test_frontend_with_auth():
    """Prueba el frontend con sesión autenticada"""
    print("\n🔍 VERIFICACIÓN DE FRONTEND CON AUTENTICACIÓN")
    print("=" * 60)
    
    # Realizar login
    session = login_and_get_session()
    if not session:
        print("❌ No se pudo autenticar")
        return False
    
    # Verificar página professional con sesión autenticada
    try:
        professional_response = session.get("http://localhost:5000/professional", timeout=10)
        print(f"📊 Status Code: {professional_response.status_code}")
        
        if professional_response.status_code == 200:
            html_content = professional_response.text
            
            # Verificar elementos HTML necesarios
            elementos_requeridos = [
                'id="sugerenciasTratamiento"',
                'id="listaSugerenciasTratamiento"',
                'sugerirTratamientoConIA()'
            ]
            
            elementos_encontrados = []
            for elemento in elementos_requeridos:
                if elemento in html_content:
                    elementos_encontrados.append(elemento)
                    print(f"✅ Elemento encontrado: {elemento}")
                else:
                    print(f"❌ Elemento NO encontrado: {elemento}")
            
            if len(elementos_encontrados) == len(elementos_requeridos):
                print("✅ Todos los elementos HTML están presentes")
                return True
            else:
                print(f"❌ Faltan {len(elementos_requeridos) - len(elementos_encontrados)} elementos")
                return False
        else:
            print(f"❌ Error accediendo a professional: {professional_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando frontend: {e}")
        return False

def test_endpoints_with_auth():
    """Prueba los endpoints con sesión autenticada"""
    print("\n🔧 VERIFICACIÓN DE ENDPOINTS CON AUTENTICACIÓN")
    print("=" * 60)
    
    # Realizar login
    session = login_and_get_session()
    if not session:
        print("❌ No se pudo autenticar")
        return False
    
    # Probar endpoint de generación de términos
    print("📋 Probando endpoint de generación de términos...")
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

def test_complete_flow_with_auth():
    """Prueba el flujo completo con autenticación"""
    print("\n🔄 PRUEBA DE FLUJO COMPLETO CON AUTENTICACIÓN")
    print("=" * 60)
    
    # Realizar login
    session = login_and_get_session()
    if not session:
        print("❌ No se pudo autenticar")
        return False
    
    # Simular el flujo completo
    print("1️⃣ Generando términos disponibles...")
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
                
                # Simular selección de términos
                terminos_seleccionados = recomendados[:3] if len(recomendados) >= 3 else recomendados
                print(f"2️⃣ Simulando selección: {terminos_seleccionados}")
                
                # Probar búsqueda con términos seleccionados
                print("3️⃣ Probando búsqueda con términos seleccionados...")
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
    print("🔍 VERIFICACIÓN COMPLETA CON AUTENTICACIÓN")
    print("=" * 60)
    
    # Ejecutar todas las verificaciones
    resultados = []
    
    # Verificar frontend con auth
    resultados.append(("Frontend con Auth", test_frontend_with_auth()))
    
    # Verificar endpoints con auth
    resultados.append(("Endpoints con Auth", test_endpoints_with_auth()))
    
    # Verificar flujo completo con auth
    resultados.append(("Flujo Completo con Auth", test_complete_flow_with_auth()))
    
    # Mostrar resumen
    print("\n📊 RESUMEN DE VERIFICACIÓN CON AUTENTICACIÓN")
    print("=" * 50)
    
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
        print("   1. Ve a http://localhost:5000")
        print("   2. Inicia sesión como profesional")
        print("   3. Ve a la sección de atención")
        print("   4. Llena un diagnóstico (ej: 'Dolor lumbar')")
        print("   5. Haz clic en 'Sugerir Tratamiento con IA'")
        print("   6. Deberías ver los términos de búsqueda para seleccionar")
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("❌ Revisa los errores anteriores")

if __name__ == "__main__":
    main() 