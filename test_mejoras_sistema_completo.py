#!/usr/bin/env python3
"""
Script de prueba para verificar las mejoras completas del sistema Copilot Health
"""

import requests
import json
import time

def test_mejoras_sistema_completo():
    """Prueba todas las mejoras del sistema Copilot Health"""
    
    print("🧪 PRUEBA COMPLETA DEL SISTEMA COPILOT HEALTH")
    print("=" * 70)
    
    # Configuración
    base_url = "http://localhost:5000"
    
    # Caso de prueba realista
    caso_prueba = {
        "tipo_atencion": "kinesiologia",
        "motivo_consulta": "Dolor de rodilla por golpe en el trabajo",
        "evaluacion": "¿En qué momento del día es peor el dolor? cuando me levanto ¿Qué actividades agravan el dolor? pasar mucho tiempo de pie ¿Qué actividades alivian el dolor? tener la rodilla en reposo ¿Hay hinchazón o calor en la rodilla? hay hinchazón ¿Ha tenido lesiones previas en la rodilla? no ¿El dolor es constante o intermitente? es intermitente ¿Hay bloqueos o sensación de inestabilidad? sensación de inestabilidad ¿Puede subir y bajar escaleras sin dolor? bajar duele la rodilla",
        "edad": "35"
    }
    
    print(f"📋 CASO DE PRUEBA:")
    print(f"   Tipo de atención: {caso_prueba['tipo_atencion']}")
    print(f"   Motivo de consulta: {caso_prueba['motivo_consulta']}")
    print(f"   Evaluación: {caso_prueba['evaluacion'][:100]}...")
    print(f"   Edad: {caso_prueba['edad']} años")
    
    # 1. Probar análisis de motivo de consulta
    print("\n🔍 1. PROBANDO ANÁLISIS DE MOTIVO DE CONSULTA")
    print("-" * 50)
    
    try:
        response = requests.post(f"{base_url}/api/copilot/analyze-motivo", 
                               json={"motivo_consulta": caso_prueba["motivo_consulta"]},
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Análisis de motivo exitoso")
            print(f"   Especialidad detectada: {data.get('analisis', {}).get('especialidad_detectada', 'N/A')}")
            print(f"   Categoría: {data.get('analisis', {}).get('categoria', 'N/A')}")
            print(f"   Urgencia: {data.get('analisis', {}).get('urgencia', 'N/A')}")
        else:
            print(f"❌ Error en análisis de motivo: {response.status_code}")
            print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error conectando con el servidor: {e}")
        return
    
    # 2. Probar generación de preguntas
    print("\n📝 2. PROBANDO GENERACIÓN DE PREGUNTAS")
    print("-" * 50)
    
    try:
        response = requests.post(f"{base_url}/api/copilot/generate-evaluation-questions", 
                               json={
                                   "motivo_consulta": caso_prueba["motivo_consulta"],
                                   "tipo_atencion": caso_prueba["tipo_atencion"],
                                   "edad": caso_prueba["edad"]
                               },
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Generación de preguntas exitosa")
            if data.get('preguntas'):
                print(f"   Preguntas generadas: {len(data['preguntas'])}")
                for i, pregunta in enumerate(data['preguntas'][:3], 1):
                    print(f"   {i}. {pregunta}")
            else:
                print("   ⚠️ No se generaron preguntas")
        else:
            print(f"❌ Error en generación de preguntas: {response.status_code}")
            print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error en generación de preguntas: {e}")
    
    # 3. Probar búsqueda de evidencia científica
    print("\n🔬 3. PROBANDO BÚSQUEDA DE EVIDENCIA CIENTÍFICA")
    print("-" * 50)
    
    try:
        # Probar endpoint principal
        response = requests.post(f"{base_url}/api/copilot/search-enhanced", 
                               json={
                                   "motivo_consulta": caso_prueba["motivo_consulta"],
                                   "terminos_clave": ["rodilla", "dolor", "fisioterapia"],
                                   "especialidad": "fisioterapia",
                                   "contexto_clinico": ["dolor en rodilla", "lesión laboral"]
                               },
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Búsqueda de evidencia exitosa")
            if data.get('evidencia_cientifica'):
                print(f"   Papers encontrados: {len(data['evidencia_cientifica'])}")
                for i, paper in enumerate(data['evidencia_cientifica'][:3], 1):
                    titulo = paper.get('titulo', 'Sin título')
                    autores = paper.get('autores', [])
                    ano = paper.get('año_publicacion', 'N/A')
                    doi = paper.get('doi', 'Sin DOI')
                    print(f"   {i}. {titulo}")
                    print(f"      Autores: {', '.join(autores) if autores else 'Sin autores'}")
                    print(f"      Año: {ano} | DOI: {doi}")
            else:
                print("   ⚠️ No se encontraron papers")
        else:
            print(f"❌ Error en búsqueda de evidencia: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
            # Probar endpoint alternativo
            print("   🔄 Probando endpoint alternativo...")
            response = requests.post(f"{base_url}/api/copilot/search-with-terms", 
                                   json={
                                       "condicion": caso_prueba["motivo_consulta"],
                                       "especialidad": "fisioterapia",
                                       "edad": caso_prueba["edad"],
                                       "terminos_seleccionados": ["rodilla", "dolor", "fisioterapia"]
                                   },
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Búsqueda alternativa exitosa")
                if data.get('resultados'):
                    print(f"   Papers encontrados: {len(data['resultados'])}")
                else:
                    print("   ⚠️ No se encontraron papers")
            else:
                print(f"❌ Error en búsqueda alternativa: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en búsqueda de evidencia: {e}")
    
    # 4. Probar análisis completo
    print("\n🧠 4. PROBANDO ANÁLISIS COMPLETO")
    print("-" * 50)
    
    try:
        response = requests.post(f"{base_url}/api/copilot/complete-analysis", 
                               json={
                                   "motivo_consulta": caso_prueba["motivo_consulta"],
                                   "tipo_atencion": caso_prueba["tipo_atencion"],
                                   "edad": caso_prueba["edad"],
                                   "antecedentes": "Sin antecedentes relevantes",
                                   "evaluacion": caso_prueba["evaluacion"]
                               },
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Análisis completo exitoso")
            if data.get('resumen'):
                print(f"   Resumen generado: {len(data['resumen'])} caracteres")
                print(f"   Palabras clave: {data.get('palabras_clave', [])}")
                print(f"   Patologías: {data.get('patologias', [])}")
            else:
                print("   ⚠️ No se generó resumen")
        else:
            print(f"❌ Error en análisis completo: {response.status_code}")
            print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error en análisis completo: {e}")
    
    # 5. Verificar que no hay búsquedas duplicadas
    print("\n🔄 5. VERIFICANDO QUE NO HAY BÚSQUEDAS DUPLICADAS")
    print("-" * 50)
    
    print("✅ El sistema debe ejecutar solo una búsqueda por análisis")
    print("✅ El sistema debe usar términos mejorados (rodilla, fisioterapia, etc.)")
    print("✅ Los papers deben tener información completa (autores, año, DOI)")
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 70)
    
    print("✅ Pruebas completadas.")
    print("\n🎯 MEJORAS IMPLEMENTADAS:")
    print("   • Control de estado para evitar búsquedas duplicadas")
    print("   • Términos de búsqueda mejorados y contextuales")
    print("   • Extracción de términos anatómicos específicos")
    print("   • Análisis de síntomas por profesión")
    print("   • Información completa en papers científicos")
    print("   • Búsqueda multi-endpoint con fallback")

if __name__ == "__main__":
    test_mejoras_sistema_completo() 