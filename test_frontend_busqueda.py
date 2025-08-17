#!/usr/bin/env python3
"""
Script para probar la funcionalidad del frontend con búsqueda real
"""

import requests
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_busqueda():
    """Prueba la API de búsqueda directamente"""
    print("🔍 PRUEBA DE API DE BÚSQUEDA")
    print("=" * 40)
    
    # Simular una petición del frontend
    url = "http://localhost:5000/api/copilot/suggest-treatment"
    
    # Datos de prueba
    data = {
        'motivo_atencion': 'Dolor lumbar de 3 semanas',
        'tipo_atencion': 'kinesiologia',
        'evaluacion_observaciones': 'Paciente presenta dolor lumbar de 3 semanas de evolución, con irradiación hacia la pierna izquierda. El dolor es peor al estar sentado y mejora con la posición fetal.'
    }
    
    try:
        print("🔍 Enviando petición de búsqueda...")
        response = requests.post(url, json=data, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                resultado = response.json()
                print("✅ Respuesta JSON válida")
                
                # Verificar estructura de la respuesta
                if 'tratamientos_cientificos' in resultado:
                    tratamientos = resultado['tratamientos_cientificos']
                    print(f"✅ Encontrados {len(tratamientos)} tratamientos científicos")
                    
                    if tratamientos:
                        print("\n📄 Primer tratamiento:")
                        primer_tratamiento = tratamientos[0]
                        print(f"   Título: {primer_tratamiento.get('titulo', 'Sin título')}")
                        print(f"   DOI: {primer_tratamiento.get('doi', 'Sin DOI')}")
                        print(f"   Fuente: {primer_tratamiento.get('fuente', 'Sin fuente')}")
                        print(f"   Nivel de evidencia: {primer_tratamiento.get('nivel_evidencia', 'Sin nivel')}")
                    else:
                        print("⚠️ No hay tratamientos en la respuesta")
                else:
                    print("❌ No hay 'tratamientos_cientificos' en la respuesta")
                    print(f"Estructura de respuesta: {list(resultado.keys())}")
                
                # Verificar plan de intervención
                if 'plan_intervencion' in resultado:
                    plan = resultado['plan_intervencion']
                    print(f"\n📋 Plan de intervención:")
                    print(f"   Título: {plan.get('titulo', 'Sin título')}")
                    print(f"   Técnicas específicas: {len(plan.get('tecnicas_especificas', []))}")
                    print(f"   Ejercicios específicos: {len(plan.get('ejercicios_especificos', []))}")
                else:
                    print("❌ No hay 'plan_intervencion' en la respuesta")
                
                # Verificar preguntas científicas
                if 'preguntas_cientificas' in resultado:
                    preguntas = resultado['preguntas_cientificas']
                    print(f"\n❓ Preguntas científicas: {len(preguntas)}")
                    if preguntas:
                        print(f"   Primera pregunta: {preguntas[0][:100]}...")
                else:
                    print("❌ No hay 'preguntas_cientificas' en la respuesta")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"Respuesta: {response.text[:200]}...")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Respuesta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_api_preguntas():
    """Prueba la API de generación de preguntas"""
    print("\n❓ PRUEBA DE API DE PREGUNTAS")
    print("=" * 40)
    
    url = "http://localhost:5000/api/copilot/generate-evaluation-questions"
    
    data = {
        'motivo_atencion': 'Dolor lumbar de 3 semanas',
        'tipo_atencion': 'kinesiologia'
    }
    
    try:
        print("🔍 Enviando petición de preguntas...")
        response = requests.post(url, json=data, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                resultado = response.json()
                print("✅ Respuesta JSON válida")
                
                if 'preguntas' in resultado:
                    preguntas = resultado['preguntas']
                    print(f"✅ Generadas {len(preguntas)} preguntas")
                    
                    for i, pregunta in enumerate(preguntas, 1):
                        print(f"   {i}. {pregunta}")
                else:
                    print("❌ No hay 'preguntas' en la respuesta")
                    print(f"Estructura: {list(resultado.keys())}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_frontend_simulado():
    """Simula las llamadas del frontend"""
    print("\n🖥️ PRUEBA FRONTEND SIMULADO")
    print("=" * 40)
    
    # Simular la búsqueda de pacientes
    url_pacientes = "http://localhost:5000/api/professional/patients"
    
    try:
        print("🔍 Obteniendo lista de pacientes...")
        response = requests.get(url_pacientes, timeout=10)
        
        if response.status_code == 200:
            try:
                pacientes = response.json()
                print(f"✅ Encontrados {len(pacientes)} pacientes")
                
                if pacientes:
                    primer_paciente = pacientes[0]
                    print(f"📄 Primer paciente: {primer_paciente.get('nombre_completo', 'Sin nombre')}")
                    
                    # Simular búsqueda de tratamientos para este paciente
                    test_busqueda_paciente(primer_paciente.get('nombre_completo', 'Paciente'))
                else:
                    print("⚠️ No hay pacientes disponibles")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error obteniendo pacientes: {e}")

def test_busqueda_paciente(nombre_paciente):
    """Prueba búsqueda para un paciente específico"""
    print(f"\n🔍 Probando búsqueda para: {nombre_paciente}")
    
    url = "http://localhost:5000/api/copilot/suggest-treatment"
    
    data = {
        'motivo_atencion': 'Dolor en rodilla al caminar',
        'tipo_atencion': 'kinesiologia',
        'evaluacion_observaciones': 'Paciente refiere dolor en rodilla derecha al caminar, con limitación de movilidad y crepitación articular.'
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            resultado = response.json()
            
            if 'tratamientos_cientificos' in resultado:
                tratamientos = resultado['tratamientos_cientificos']
                print(f"✅ Encontrados {len(tratamientos)} tratamientos para {nombre_paciente}")
                
                if tratamientos:
                    print("📄 Tratamientos encontrados:")
                    for i, tratamiento in enumerate(tratamientos[:3], 1):  # Mostrar solo los primeros 3
                        print(f"   {i}. {tratamiento.get('titulo', 'Sin título')[:80]}...")
            else:
                print("❌ No se encontraron tratamientos")
        else:
            print(f"❌ Error en búsqueda: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")

def main():
    """Función principal"""
    print("🔍 PRUEBAS DE FRONTEND CON BÚSQUEDA REAL")
    print("=" * 50)
    
    # Probar API de búsqueda
    test_api_busqueda()
    
    # Probar API de preguntas
    test_api_preguntas()
    
    # Probar frontend simulado
    test_frontend_simulado()
    
    print("\n✅ Todas las pruebas completadas")

if __name__ == "__main__":
    main() 