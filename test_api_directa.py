#!/usr/bin/env python3
"""
Script para probar directamente las APIs del backend
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration

def test_busqueda_directa():
    """Prueba la búsqueda directamente en el backend"""
    print("🔍 PRUEBA DE BÚSQUEDA DIRECTA EN BACKEND")
    print("=" * 50)
    
    apis = MedicalAPIsIntegration()
    
    # Casos de prueba
    casos_prueba = [
        {
            'condicion': 'Dolor lumbar de 3 semanas',
            'especialidad': 'kinesiologia',
            'descripcion': 'Dolor lumbar con irradiación hacia pierna izquierda'
        },
        {
            'condicion': 'Dificultad para tragar alimentos',
            'especialidad': 'fonoaudiologia',
            'descripcion': 'Problemas de deglución con tos al comer'
        },
        {
            'condicion': 'Ansiedad y estrés laboral',
            'especialidad': 'psicologia',
            'descripcion': 'Ansiedad generalizada con síntomas físicos'
        }
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n🔍 Caso {i}: {caso['condicion']} en {caso['especialidad']}")
        print("-" * 60)
        
        try:
            resultados = apis.obtener_tratamientos_completos(caso['condicion'], caso['especialidad'])
            
            total_pubmed = len(resultados.get('tratamientos_pubmed', []))
            total_europepmc = len(resultados.get('tratamientos_europepmc', []))
            total_preguntas = len(resultados.get('preguntas_cientificas', []))
            
            print(f"✅ Resultados PubMed: {total_pubmed}")
            print(f"✅ Resultados Europe PMC: {total_europepmc}")
            print(f"✅ Preguntas científicas: {total_preguntas}")
            print(f"✅ Total tratamientos: {total_pubmed + total_europepmc}")
            
            if total_pubmed + total_europepmc > 0:
                print("✅ Búsqueda exitosa")
                
                # Mostrar algunos resultados
                todos_tratamientos = resultados.get('tratamientos_pubmed', []) + resultados.get('tratamientos_europepmc', [])
                
                if todos_tratamientos:
                    print("\n📄 Primeros tratamientos encontrados:")
                    for j, tratamiento in enumerate(todos_tratamientos[:3], 1):
                        print(f"   {j}. {tratamiento.titulo[:80]}...")
                        print(f"      DOI: {tratamiento.doi}")
                        print(f"      Fuente: {tratamiento.fuente}")
                        print()
            else:
                print("⚠️ No se encontraron tratamientos")
                
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")

def test_preguntas_directa():
    """Prueba la generación de preguntas directamente"""
    print("\n❓ PRUEBA DE PREGUNTAS DIRECTA")
    print("=" * 40)
    
    apis = MedicalAPIsIntegration()
    
    casos_preguntas = [
        {
            'motivo': 'Dolor lumbar de 3 semanas',
            'tipo': 'kinesiologia'
        },
        {
            'motivo': 'Dificultad para tragar',
            'tipo': 'fonoaudiologia'
        },
        {
            'motivo': 'Ansiedad y estrés',
            'tipo': 'psicologia'
        }
    ]
    
    for i, caso in enumerate(casos_preguntas, 1):
        print(f"\n🔍 Caso {i}: {caso['motivo']} en {caso['tipo']}")
        print("-" * 50)
        
        try:
            preguntas = apis.generar_preguntas_personalizadas_evaluacion(caso['motivo'], caso['tipo'])
            
            print(f"✅ Generadas {len(preguntas)} preguntas")
            
            for j, pregunta in enumerate(preguntas[:5], 1):
                print(f"   {j}. {pregunta}")
                
        except Exception as e:
            print(f"❌ Error generando preguntas: {e}")

def test_plan_intervencion():
    """Prueba la generación de planes de intervención"""
    print("\n📋 PRUEBA DE PLANES DE INTERVENCIÓN")
    print("=" * 50)
    
    apis = MedicalAPIsIntegration()
    
    # Simular algunos tratamientos encontrados
    from medical_apis_integration import TratamientoCientifico
    
    tratamientos_simulados = [
        TratamientoCientifico(
            titulo="Physical Therapy for Low Back Pain",
            descripcion="Evidence-based physical therapy interventions for chronic low back pain",
            doi="10.1002/14651858.CD001254",
            fuente="Europe PMC",
            tipo_evidencia="Systematic Review",
            fecha_publicacion="2023",
            autores=["Smith J", "Johnson A"],
            resumen="Systematic review of physical therapy interventions for low back pain",
            keywords=["low back pain", "physical therapy", "rehabilitation"]
        )
    ]
    
    try:
        plan = apis._generar_plan_intervencion_especifico(
            "Dolor lumbar de 3 semanas",
            "kinesiologia",
            tratamientos_simulados
        )
        
        print(f"✅ Plan de intervención generado:")
        print(f"   Título: {plan.titulo}")
        print(f"   Técnicas específicas: {len(plan.tecnicas_especificas)}")
        print(f"   Ejercicios específicos: {len(plan.ejercicios_especificos)}")
        print(f"   Protocolo de tratamiento: {len(plan.protocolo_tratamiento)}")
        print(f"   Nivel de evidencia: {plan.nivel_evidencia}")
        
        print("\n📋 Técnicas específicas:")
        for i, tecnica in enumerate(plan.tecnicas_especificas[:3], 1):
            print(f"   {i}. {tecnica}")
            
    except Exception as e:
        print(f"❌ Error generando plan: {e}")

def main():
    """Función principal"""
    print("🔍 PRUEBAS DIRECTAS DEL BACKEND")
    print("=" * 50)
    
    # Probar búsqueda directa
    test_busqueda_directa()
    
    # Probar preguntas directa
    test_preguntas_directa()
    
    # Probar planes de intervención
    test_plan_intervencion()
    
    print("\n✅ Todas las pruebas completadas")

if __name__ == "__main__":
    main() 