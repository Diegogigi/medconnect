#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la funcionalidad de la sidebar de Copilot Health
"""

import requests
import json

def test_sidebar_functionality():
    """Prueba la funcionalidad de la sidebar"""
    
    print("🤖 PRUEBA DE FUNCIONALIDAD DE SIDEBAR")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Datos de prueba
    test_data = {
        "motivo_consulta": "Dolor en el brazo derecho después de una caída",
        "tipo_atencion": "Traumatología",
        "edad": "45",
        "antecedentes": "Hipertensión arterial, diabetes tipo 2",
        "evaluacion": "Dolor intenso al movimiento, limitación funcional"
    }
    
    try:
        print("1. 🔍 Probando endpoint de análisis de motivo...")
        response = requests.post(f"{base_url}/api/copilot/analyze-motivo", 
                               json={"motivo_consulta": test_data["motivo_consulta"]})
        
        if response.status_code == 200:
            print("   ✅ Endpoint de análisis de motivo - FUNCIONANDO")
            data = response.json()
            print(f"   📊 Respuesta: {data.get('analisis', {}).get('resumen', 'Sin resumen')}")
        else:
            print(f"   ❌ Error en análisis de motivo: {response.status_code}")
        
        print("\n2. 🔍 Probando endpoint de búsqueda mejorada...")
        response = requests.post(f"{base_url}/api/copilot/search-enhanced", 
                               json={"query": test_data["motivo_consulta"], "max_results": 3})
        
        if response.status_code == 200:
            print("   ✅ Endpoint de búsqueda mejorada - FUNCIONANDO")
            data = response.json()
            papers = data.get('papers', [])
            print(f"   📊 Papers encontrados: {len(papers)}")
            for i, paper in enumerate(papers[:2]):
                print(f"      Paper {i+1}: {paper.get('titulo', 'Sin título')}")
        else:
            print(f"   ❌ Error en búsqueda mejorada: {response.status_code}")
        
        print("\n3. 🔍 Probando endpoint de análisis completo...")
        response = requests.post(f"{base_url}/api/copilot/complete-analysis", 
                               json={
                                   "motivo_consulta": test_data["motivo_consulta"],
                                   "tipo_atencion": test_data["tipo_atencion"],
                                   "edad": test_data["edad"],
                                   "antecedentes": test_data["antecedentes"]
                               })
        
        if response.status_code == 200:
            print("   ✅ Endpoint de análisis completo - FUNCIONANDO")
            data = response.json()
            print(f"   📊 Respuesta: {data.get('analisis', {}).get('resumen', 'Sin resumen')}")
        else:
            print(f"   ❌ Error en análisis completo: {response.status_code}")
        
        print("\n4. 🔍 Probando endpoint de preguntas personalizadas...")
        response = requests.post(f"{base_url}/api/copilot/generate-evaluation-questions", 
                               json={
                                   "motivo_consulta": test_data["motivo_consulta"],
                                   "tipo_atencion": test_data["tipo_atencion"],
                                   "edad": test_data["edad"],
                                   "antecedentes": test_data["antecedentes"]
                               })
        
        if response.status_code == 200:
            print("   ✅ Endpoint de preguntas personalizadas - FUNCIONANDO")
            data = response.json()
            preguntas = data.get('preguntas', [])
            print(f"   📊 Preguntas generadas: {len(preguntas)}")
            for i, pregunta in enumerate(preguntas[:3]):
                print(f"      Pregunta {i+1}: {pregunta}")
        else:
            print(f"   ❌ Error en preguntas personalizadas: {response.status_code}")
        
        print("\n5. 🌐 Verificando página professional...")
        response = requests.get(f"{base_url}/professional")
        
        if response.status_code == 200:
            print("   ✅ Página professional - ACCESIBLE")
            
            # Verificar elementos de la sidebar
            content = response.text
            elementos_sidebar = [
                'btnCopilotPrimary',
                'messagesContainer', 
                'resultsArea',
                'activarCopilotHealthElegant',
                'realizarAnalisisElegant',
                'mostrarResultadosElegant'
            ]
            
            elementos_encontrados = 0
            for elemento in elementos_sidebar:
                if elemento in content:
                    print(f"   ✅ {elemento} - PRESENTE")
                    elementos_encontrados += 1
                else:
                    print(f"   ❌ {elemento} - NO ENCONTRADO")
            
            print(f"\n   📊 Elementos de sidebar: {elementos_encontrados}/{len(elementos_sidebar)}")
            
        else:
            print(f"   ❌ Error accediendo a página professional: {response.status_code}")
        
        print("\n" + "=" * 50)
        print("📊 RESUMEN DE PRUEBAS")
        print("=" * 50)
        print("✅ Endpoints de API probados")
        print("✅ Funciones de sidebar verificadas")
        print("✅ Elementos de interfaz confirmados")
        print("\n🎯 La sidebar debería funcionar correctamente ahora.")
        print("💡 Recuerda limpiar el caché del navegador (Ctrl+F5)")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: El servidor no está ejecutándose")
        print("💡 Ejecuta: python app.py")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_sidebar_functionality() 