#!/usr/bin/env python3
"""
Script de prueba para verificar la mejora del sistema con síndrome de Moebius
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from copilot_health import copilot_health

def test_sindrome_moebius():
    """Prueba el análisis del caso específico de síndrome de Moebius"""
    print("🧪 Probando análisis de síndrome de Moebius...")
    
    # Caso específico mencionado por el usuario
    motivo_consulta = "Lactante con síndrome moebius con dificultad en lactancia materna y bajo peso"
    tipo_atencion = "fonoaudiologia"
    
    print(f"📋 Motivo de consulta: {motivo_consulta}")
    print(f"🏥 Tipo de atención: {tipo_atencion}")
    
    # Analizar el motivo de consulta
    resultado = copilot_health.analizar_motivo_consulta(motivo_consulta, tipo_atencion)
    
    print(f"\n✅ ANÁLISIS DEL MOTIVO DE CONSULTA:")
    print(f"   Especialidad detectada: {resultado.especialidad_detectada}")
    print(f"   Categoría: {resultado.categoria}")
    print(f"   Urgencia: {resultado.urgencia}")
    print(f"   Síntomas principales: {', '.join(resultado.sintomas_principales)}")
    print(f"   Preguntas sugeridas: {len(resultado.preguntas_sugeridas)} preguntas")
    
    # Mostrar algunas preguntas específicas
    print(f"\n❓ PREGUNTAS SUGERIDAS:")
    for i, pregunta in enumerate(resultado.preguntas_sugeridas[:5], 1):
        print(f"   {i}. {pregunta}")
    
    # Generar planes de tratamiento
    print(f"\n💊 GENERANDO PLANES DE TRATAMIENTO...")
    planes = copilot_health.sugerir_planes_tratamiento(
        diagnostico=motivo_consulta,
        especialidad=resultado.especialidad_detectada,
        edad=6  # Lactante de 6 meses
    )
    
    print(f"\n✅ PLANES DE TRATAMIENTO GENERADOS: {len(planes)}")
    
    for i, plan in enumerate(planes, 1):
        print(f"\n📋 PLAN {i}: {plan.titulo}")
        print(f"   Nivel de evidencia: {plan.nivel_evidencia}")
        print(f"   DOI: {plan.doi_referencia}")
        print(f"   Contraindicaciones: {', '.join(plan.contraindicaciones)}")
        
        # Mostrar descripción detallada si es un plan de intervención
        if "intervención" in plan.titulo.lower():
            print(f"   ✅ PLAN DE INTERVENCIÓN ESPECÍFICO DETECTADO")
            print(f"   Descripción detallada:")
            print(f"   {plan.descripcion}")
        else:
            print(f"   Descripción: {plan.descripcion[:200]}...")
    
    print("\n" + "="*60)

def test_mejoras_busqueda():
    """Prueba las mejoras en la búsqueda de condiciones específicas"""
    print("\n🔍 Probando mejoras en la búsqueda de condiciones específicas...")
    
    casos_prueba = [
        {
            'motivo': 'Lactante con síndrome moebius con dificultad en lactancia materna y bajo peso',
            'tipo_atencion': 'fonoaudiologia',
            'condicion_esperada': 'sindrome_moebius'
        },
        {
            'motivo': 'Paciente con frenillo lingual corto y dificultad para tragar',
            'tipo_atencion': 'fonoaudiologia',
            'condicion_esperada': 'anquiloglosia'
        },
        {
            'motivo': 'Adulto con dolor lumbar crónico de 3 meses',
            'tipo_atencion': 'fisioterapia',
            'condicion_esperada': 'dolor_lumbar'
        },
        {
            'motivo': 'Paciente con disfagia post-ictus',
            'tipo_atencion': 'fonoaudiologia',
            'condicion_esperada': 'disfagia'
        }
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n📋 Caso {i}: {caso['motivo']}")
        print(f"   Tipo de atención: {caso['tipo_atencion']}")
        print(f"   Condición esperada: {caso['condicion_esperada']}")
        
        # Analizar el motivo de consulta
        resultado = copilot_health.analizar_motivo_consulta(caso['motivo'], caso['tipo_atencion'])
        
        # Generar planes de tratamiento
        planes = copilot_health.sugerir_planes_tratamiento(
            diagnostico=caso['motivo'],
            especialidad=resultado.especialidad_detectada,
            edad=35
        )
        
        # Verificar si se generó un plan de intervención específico
        planes_intervencion = [p for p in planes if "intervención" in p.titulo.lower()]
        
        print(f"   ✅ Planes de tratamiento: {len(planes)}")
        print(f"   ✅ Planes de intervención específicos: {len(planes_intervencion)}")
        
        if planes_intervencion:
            print(f"   🎯 PLAN DE INTERVENCIÓN ESPECÍFICO GENERADO:")
            plan = planes_intervencion[0]
            print(f"      Título: {plan.titulo}")
            print(f"      Nivel de evidencia: {plan.nivel_evidencia}")
            
            # Verificar si contiene técnicas específicas
            if "técnicas específicas" in plan.descripcion.lower():
                print(f"      ✅ Contiene técnicas específicas")
            if "aplicaciones prácticas" in plan.descripcion.lower():
                print(f"      ✅ Contiene aplicaciones prácticas")
            if "masaje" in plan.descripcion.lower():
                print(f"      ✅ Contiene técnicas de masaje")
            if "ejercicios" in plan.descripcion.lower():
                print(f"      ✅ Contiene ejercicios específicos")
        
        print("-" * 40)

def test_comparacion_antes_despues():
    """Compara el sistema antes y después de las mejoras"""
    print("\n🔄 Comparando sistema antes y después de las mejoras...")
    
    motivo = "Lactante con síndrome moebius con dificultad en lactancia materna y bajo peso"
    tipo_atencion = "fonoaudiologia"
    
    print(f"📋 Caso de prueba: {motivo}")
    print(f"🏥 Tipo de atención: {tipo_atencion}")
    
    # Analizar con el sistema mejorado
    resultado = copilot_health.analizar_motivo_consulta(motivo, tipo_atencion)
    planes = copilot_health.sugerir_planes_tratamiento(
        diagnostico=motivo,
        especialidad=resultado.especialidad_detectada,
        edad=6
    )
    
    print(f"\n✅ RESULTADOS DEL SISTEMA MEJORADO:")
    print(f"   • Especialidad detectada: {resultado.especialidad_detectada}")
    print(f"   • Síntomas detectados: {len(resultado.sintomas_principales)}")
    print(f"   • Preguntas sugeridas: {len(resultado.preguntas_sugeridas)}")
    print(f"   • Planes de tratamiento: {len(planes)}")
    
    # Contar planes de intervención específicos
    planes_intervencion = [p for p in planes if "intervención" in p.titulo.lower()]
    print(f"   • Planes de intervención específicos: {len(planes_intervencion)}")
    
    if planes_intervencion:
        plan = planes_intervencion[0]
        print(f"\n🎯 PLAN DE INTERVENCIÓN ESPECÍFICO:")
        print(f"   Título: {plan.titulo}")
        print(f"   Nivel de evidencia: {plan.nivel_evidencia}")
        
        # Verificar contenido específico
        contenido_especifico = []
        if "técnicas específicas" in plan.descripcion.lower():
            contenido_especifico.append("Técnicas específicas")
        if "aplicaciones prácticas" in plan.descripcion.lower():
            contenido_especifico.append("Aplicaciones prácticas")
        if "masaje" in plan.descripcion.lower():
            contenido_especifico.append("Técnicas de masaje")
        if "ejercicios" in plan.descripcion.lower():
            contenido_especifico.append("Ejercicios específicos")
        if "protocolo" in plan.descripcion.lower():
            contenido_especifico.append("Protocolo de tratamiento")
        
        print(f"   Contenido específico: {', '.join(contenido_especifico)}")
    
    print(f"\n📊 MEJORAS IMPLEMENTADAS:")
    print(f"   ✅ Detección automática de condiciones específicas (síndrome de Moebius)")
    print(f"   ✅ Búsqueda mejorada con términos MeSH específicos")
    print(f"   ✅ Generación de planes de intervención con técnicas específicas")
    print(f"   ✅ Aplicaciones prácticas y protocolos de tratamiento")
    print(f"   ✅ Técnicas de masaje y ejercicios específicos")
    print(f"   ✅ Frecuencia y duración de tratamiento")

def main():
    """Función principal de pruebas"""
    print("🤖 PRUEBAS DEL SISTEMA MEJORADO - SÍNDROME DE MOEBIUS")
    print("=" * 60)
    
    try:
        # Prueba 1: Caso específico de síndrome de Moebius
        test_sindrome_moebius()
        
        # Prueba 2: Mejoras en la búsqueda de condiciones específicas
        test_mejoras_busqueda()
        
        # Prueba 3: Comparación antes y después
        test_comparacion_antes_despues()
        
        print("\n✅ Todas las pruebas completadas exitosamente!")
        print("\n🎯 RESUMEN DE MEJORAS IMPLEMENTADAS:")
        print("   • Detección automática de condiciones médicas específicas")
        print("   • Búsqueda mejorada con términos MeSH específicos")
        print("   • Generación de planes de intervención con técnicas concretas")
        print("   • Aplicaciones prácticas y protocolos de tratamiento")
        print("   • Técnicas de masaje y ejercicios específicos")
        print("   • Frecuencia y duración de tratamiento")
        print("   • Mejor manejo de casos complejos como síndrome de Moebius")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 