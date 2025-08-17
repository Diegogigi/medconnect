#!/usr/bin/env python3
"""
Script para debuggear el problema de términos que no aparecen en el frontend
"""

import requests
import json

def test_endpoint_generate_terms():
    """Prueba el endpoint de generación de términos directamente"""
    print("🔍 PRUEBA DIRECTA DEL ENDPOINT DE TÉRMINOS")
    print("=" * 50)
    
    # Simular una sesión autenticada (esto es solo para prueba)
    session = requests.Session()
    
    # Datos de prueba
    test_data = {
        'condicion': 'Dolor lumbar de 3 semanas',
        'especialidad': 'kinesiologia',
        'edad': 70
    }
    
    print(f"📋 Datos de prueba: {test_data}")
    
    try:
        # Intentar llamar al endpoint
        response = session.post(
            "http://localhost:5000/api/copilot/generate-search-terms",
            json=test_data,
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

def test_frontend_flow():
    """Simula el flujo completo del frontend"""
    print("\n🖥️ SIMULACIÓN DEL FLUJO FRONTEND")
    print("=" * 50)
    
    # Simular los pasos que haría el frontend
    print("1️⃣ Simulando llenado de formulario...")
    diagnostico = "Dolor lumbar de 3 semanas"
    especialidad = "kinesiologia"
    edad = 70
    
    print(f"   Diagnóstico: {diagnostico}")
    print(f"   Especialidad: {especialidad}")
    print(f"   Edad: {edad}")
    
    print("\n2️⃣ Simulando llamada a API...")
    session = requests.Session()
    
    try:
        response = session.post(
            "http://localhost:5000/api/copilot/generate-search-terms",
            json={
                'condicion': diagnostico,
                'especialidad': especialidad,
                'edad': edad
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                terminos = data.get('terminos_disponibles', {})
                print("✅ API respondió correctamente")
                
                print("\n3️⃣ Simulando renderizado de términos...")
                print("   Los términos deberían mostrarse en el frontend:")
                
                # Simular lo que debería mostrar el frontend
                if terminos.get('terminos_recomendados'):
                    print("   ⭐ Términos Recomendados:")
                    for termino in terminos['terminos_recomendados'][:3]:
                        print(f"      ☐ {termino}")
                
                if terminos.get('terminos_especialidad'):
                    print("   🏥 Términos de Especialidad:")
                    for termino in terminos['terminos_especialidad'][:2]:
                        print(f"      ☐ {termino}")
                
                if terminos.get('terminos_edad'):
                    print("   👤 Términos por Edad:")
                    for termino in terminos['terminos_edad'][:2]:
                        print(f"      ☐ {termino}")
                
                print("\n✅ Flujo simulado exitoso")
                return True
            else:
                print(f"❌ Error en API: {data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en flujo: {e}")
        return False

def check_html_elements():
    """Verifica que los elementos HTML estén presentes"""
    print("\n🏗️ VERIFICACIÓN DE ELEMENTOS HTML")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:5000/professional", timeout=10)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Verificar elementos críticos
            elementos_criticos = [
                'sugerenciasTratamiento',
                'listaSugerenciasTratamiento',
                'sugerirTratamientoConIA'
            ]
            
            for elemento in elementos_criticos:
                if elemento in html_content:
                    print(f"✅ {elemento} presente en HTML")
                else:
                    print(f"❌ {elemento} NO presente en HTML")
            
            # Verificar si es página de login
            if 'login' in html_content.lower():
                print("\n⚠️ PÁGINA DE LOGIN DETECTADA")
                print("💡 Esto explica por qué no se ven los elementos")
                return False
            else:
                print("\n✅ NO ES PÁGINA DE LOGIN")
                return True
                
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🔍 DEBUGGEO COMPLETO - TÉRMINOS NO APARECEN")
    print("=" * 60)
    
    # Ejecutar todas las verificaciones
    resultados = []
    
    # Verificar endpoint
    resultados.append(("Endpoint API", test_endpoint_generate_terms()))
    
    # Verificar flujo frontend
    resultados.append(("Flujo Frontend", test_frontend_flow()))
    
    # Verificar elementos HTML
    resultados.append(("Elementos HTML", check_html_elements()))
    
    # Mostrar resumen
    print("\n📊 RESUMEN DE DEBUGGEO")
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
        print("💡 El problema puede ser:")
        print("   1. JavaScript no se ejecuta en el navegador")
        print("   2. Error en la consola del navegador")
        print("   3. Problema de autenticación en el navegador")
    else:
        print("❌ PROBLEMAS IDENTIFICADOS")
        print("❌ Revisa los errores anteriores")

if __name__ == "__main__":
    main() 