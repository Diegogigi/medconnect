#!/usr/bin/env python3
"""
Script de debug para verificar la generación de planes de intervención
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from medical_apis_integration import MedicalAPIsIntegration

def test_deteccion_condiciones():
    """Prueba la detección de condiciones específicas"""
    print("🔍 Probando detección de condiciones específicas...")
    
    apis = MedicalAPIsIntegration()
    
    casos_prueba = [
        "Lactante con síndrome moebius con dificultad en lactancia materna y bajo peso",
        "Paciente con frenillo lingual corto y dificultad para tragar",
        "Adulto con dolor lumbar crónico de 3 meses",
        "Paciente con disfagia post-ictus"
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n📋 Caso {i}: {caso}")
        condiciones = apis._detectar_condiciones_especificas(caso)
        print(f"   Condiciones detectadas: {condiciones}")
        
        # Verificar términos específicos
        for condicion in condiciones:
            if condicion in apis.condiciones_especificas:
                info = apis.condiciones_especificas[condicion]
                print(f"   ✅ {condicion}: {len(info['terminos'])} términos, {len(info['mesh_terms'])} términos MeSH")

def test_generacion_planes():
    """Prueba la generación de planes de intervención"""
    print("\n💊 Probando generación de planes de intervención...")
    
    apis = MedicalAPIsIntegration()
    
    casos_prueba = [
        {
            'condicion': "Lactante con síndrome moebius con dificultad en lactancia materna y bajo peso",
            'especialidad': 'fonoaudiologia'
        },
        {
            'condicion': "Paciente con frenillo lingual corto y dificultad para tragar",
            'especialidad': 'fonoaudiologia'
        },
        {
            'condicion': "Adulto con dolor lumbar crónico de 3 meses",
            'especialidad': 'fisioterapia'
        }
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n📋 Caso {i}: {caso['condicion']}")
        print(f"   Especialidad: {caso['especialidad']}")
        
        # Detectar condiciones
        condiciones = apis._detectar_condiciones_especificas(caso['condicion'])
        print(f"   Condiciones detectadas: {condiciones}")
        
        # Generar plan de intervención
        plan = apis._generar_plan_intervencion_especifico(
            caso['condicion'], 
            caso['especialidad'], 
            []
        )
        
        print(f"   ✅ Plan generado: {plan.titulo}")
        print(f"   Técnicas específicas: {len(plan.tecnicas_especificas)}")
        print(f"   Aplicaciones prácticas: {len(plan.aplicaciones_practicas)}")
        print(f"   Técnicas de masaje: {len(plan.masajes_tecnicas)}")
        print(f"   Ejercicios específicos: {len(plan.ejercicios_especificos)}")
        print(f"   Protocolo: {len(plan.protocolo_tratamiento)} pasos")
        
        # Mostrar algunas técnicas
        if plan.tecnicas_especificas:
            print(f"   Técnicas: {plan.tecnicas_especificas[:3]}")

def test_busqueda_mejorada():
    """Prueba la búsqueda mejorada con condiciones específicas"""
    print("\n🔍 Probando búsqueda mejorada...")
    
    apis = MedicalAPIsIntegration()
    
    condicion = "Lactante con síndrome moebius con dificultad en lactancia materna y bajo peso"
    especialidad = "fonoaudiologia"
    
    print(f"📋 Condición: {condicion}")
    print(f"🏥 Especialidad: {especialidad}")
    
    # Obtener tratamientos completos
    resultados = apis.obtener_tratamientos_completos(condicion, especialidad)
    
    print(f"\n✅ Resultados obtenidos:")
    print(f"   Tratamientos PubMed: {len(resultados.get('tratamientos_pubmed', []))}")
    print(f"   Tratamientos Europe PMC: {len(resultados.get('tratamientos_europepmc', []))}")
    print(f"   Plan de intervención: {'Sí' if resultados.get('plan_intervencion') else 'No'}")
    
    if resultados.get('plan_intervencion'):
        plan = resultados['plan_intervencion']
        print(f"\n🎯 PLAN DE INTERVENCIÓN GENERADO:")
        print(f"   Título: {plan.titulo}")
        print(f"   Técnicas específicas: {len(plan.tecnicas_especificas)}")
        print(f"   Aplicaciones prácticas: {len(plan.aplicaciones_practicas)}")
        print(f"   Técnicas de masaje: {len(plan.masajes_tecnicas)}")
        print(f"   Ejercicios específicos: {len(plan.ejercicios_especificos)}")
        
        # Mostrar técnicas específicas
        print(f"\n💡 TÉCNICAS ESPECÍFICAS:")
        for i, tecnica in enumerate(plan.tecnicas_especificas, 1):
            print(f"   {i}. {tecnica}")
        
        print(f"\n🔧 APLICACIONES PRÁCTICAS:")
        for i, aplicacion in enumerate(plan.aplicaciones_practicas, 1):
            print(f"   {i}. {aplicacion}")
        
        print(f"\n💆 TÉCNICAS DE MASAJE:")
        for i, masaje in enumerate(plan.masajes_tecnicas, 1):
            print(f"   {i}. {masaje}")
        
        print(f"\n🏃 EJERCICIOS ESPECÍFICOS:")
        for i, ejercicio in enumerate(plan.ejercicios_especificos, 1):
            print(f"   {i}. {ejercicio}")
        
        print(f"\n📋 PROTOCOLO DE TRATAMIENTO:")
        for i, paso in enumerate(plan.protocolo_tratamiento, 1):
            print(f"   {i}. {paso}")
        
        print(f"\n⏰ FRECUENCIA: {plan.frecuencia_sesiones}")
        print(f"📅 DURACIÓN: {plan.duracion_tratamiento}")

def main():
    """Función principal de debug"""
    print("🔧 DEBUG DEL SISTEMA DE PLANES DE INTERVENCIÓN")
    print("=" * 60)
    
    try:
        # Prueba 1: Detección de condiciones
        test_deteccion_condiciones()
        
        # Prueba 2: Generación de planes
        test_generacion_planes()
        
        # Prueba 3: Búsqueda mejorada
        test_busqueda_mejorada()
        
        print("\n✅ Debug completado!")
        
    except Exception as e:
        print(f"\n❌ Error durante el debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 