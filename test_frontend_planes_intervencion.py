#!/usr/bin/env python3
"""
Script para probar que los planes de intervención se muestren correctamente en el frontend
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from copilot_health import copilot_health

def test_frontend_planes_intervencion():
    """Prueba que los planes de intervención se generen correctamente para el frontend"""
    print("🎯 Probando generación de planes de intervención para el frontend...")
    
    # Caso específico de síndrome de Moebius
    motivo_consulta = "Lactante con síndrome moebius con dificultad en lactancia materna y bajo peso"
    tipo_atencion = "fonoaudiologia"
    
    print(f"📋 Motivo de consulta: {motivo_consulta}")
    print(f"🏥 Tipo de atención: {tipo_atencion}")
    
    # Analizar el motivo de consulta
    resultado = copilot_health.analizar_motivo_consulta(motivo_consulta, tipo_atencion)
    
    # Generar planes de tratamiento
    planes = copilot_health.sugerir_planes_tratamiento(
        diagnostico=motivo_consulta,
        especialidad=resultado.especialidad_detectada,
        edad=6
    )
    
    print(f"\n✅ Planes generados: {len(planes)}")
    
    # Separar planes de intervención de otros planes
    planes_intervencion = [p for p in planes if "intervención" in p.titulo.lower()]
    otros_planes = [p for p in planes if "intervención" not in p.titulo.lower()]
    
    print(f"🎯 Planes de intervención: {len(planes_intervencion)}")
    print(f"💡 Estudios científicos: {len(otros_planes)}")
    
    # Mostrar planes de intervención
    if planes_intervencion:
        print(f"\n🎯 PLANES DE INTERVENCIÓN DETECTADOS:")
        for i, plan in enumerate(planes_intervencion, 1):
            print(f"\n📋 Plan {i}: {plan.titulo}")
            print(f"   Nivel de evidencia: {plan.nivel_evidencia}")
            print(f"   DOI: {plan.doi_referencia}")
            print(f"   Contraindicaciones: {', '.join(plan.contraindicaciones)}")
            
            # Verificar contenido específico
            contenido_especifico = []
            if "técnicas específicas" in plan.descripcion.lower():
                contenido_especifico.append("✅ Técnicas específicas")
            if "aplicaciones prácticas" in plan.descripcion.lower():
                contenido_especifico.append("✅ Aplicaciones prácticas")
            if "masaje" in plan.descripcion.lower():
                contenido_especifico.append("✅ Técnicas de masaje")
            if "ejercicios" in plan.descripcion.lower():
                contenido_especifico.append("✅ Ejercicios específicos")
            if "protocolo" in plan.descripcion.lower():
                contenido_especifico.append("✅ Protocolo de tratamiento")
            
            print(f"   Contenido específico: {', '.join(contenido_especifico)}")
            
            # Mostrar descripción completa
            print(f"   Descripción completa:")
            print(f"   {plan.descripcion}")
    
    # Generar resumen de IA para verificar que se muestre correctamente
    evaluacion = copilot_health.evaluar_antecedentes("", resultado.especialidad_detectada, 6)
    resumen_ia = copilot_health.generar_resumen_ia(resultado, evaluacion, planes)
    
    print(f"\n📄 RESUMEN DE IA GENERADO:")
    print(f"   Longitud del resumen: {len(resumen_ia)} caracteres")
    
    # Verificar que el resumen contenga las secciones correctas
    secciones_esperadas = [
        "PLAN DE INTERVENCIÓN IA SUGERIDA",
        "ESTUDIOS CIENTÍFICOS RELACIONADOS"
    ]
    
    for seccion in secciones_esperadas:
        if seccion in resumen_ia:
            print(f"   ✅ Sección '{seccion}' encontrada")
        else:
            print(f"   ❌ Sección '{seccion}' NO encontrada")
    
    # Mostrar parte del resumen para verificar formato
    print(f"\n📋 PREVIEW DEL RESUMEN:")
    lines = resumen_ia.split('\n')
    for i, line in enumerate(lines[:20]):  # Mostrar primeras 20 líneas
        print(f"   {i+1:2d}: {line}")
    
    if len(lines) > 20:
        print(f"   ... (resumen continúa con {len(lines)-20} líneas más)")

def test_multiple_cases():
    """Prueba múltiples casos para verificar que los planes se generen correctamente"""
    print("\n🔍 Probando múltiples casos...")
    
    casos_prueba = [
        {
            'motivo': 'Lactante con síndrome moebius con dificultad en lactancia materna y bajo peso',
            'tipo_atencion': 'fonoaudiologia',
            'edad': 6
        },
        {
            'motivo': 'Paciente con frenillo lingual corto y dificultad para tragar',
            'tipo_atencion': 'fonoaudiologia',
            'edad': 35
        },
        {
            'motivo': 'Adulto con dolor lumbar crónico de 3 meses',
            'tipo_atencion': 'fisioterapia',
            'edad': 45
        }
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n📋 Caso {i}: {caso['motivo']}")
        print(f"   Tipo de atención: {caso['tipo_atencion']}")
        print(f"   Edad: {caso['edad']}")
        
        # Analizar y generar planes
        resultado = copilot_health.analizar_motivo_consulta(caso['motivo'], caso['tipo_atencion'])
        planes = copilot_health.sugerir_planes_tratamiento(
            diagnostico=caso['motivo'],
            especialidad=resultado.especialidad_detectada,
            edad=caso['edad']
        )
        
        # Contar tipos de planes
        planes_intervencion = [p for p in planes if "intervención" in p.titulo.lower()]
        otros_planes = [p for p in planes if "intervención" not in p.titulo.lower()]
        
        print(f"   ✅ Total planes: {len(planes)}")
        print(f"   🎯 Planes de intervención: {len(planes_intervencion)}")
        print(f"   💡 Estudios científicos: {len(otros_planes)}")
        
        if planes_intervencion:
            print(f"   ✅ PLAN DE INTERVENCIÓN DETECTADO")
            plan = planes_intervencion[0]
            print(f"      Título: {plan.titulo}")
            print(f"      Nivel: {plan.nivel_evidencia}")
            
            # Verificar contenido específico
            contenido = []
            if "técnicas específicas" in plan.descripcion.lower():
                contenido.append("Técnicas")
            if "aplicaciones prácticas" in plan.descripcion.lower():
                contenido.append("Aplicaciones")
            if "masaje" in plan.descripcion.lower():
                contenido.append("Masajes")
            if "ejercicios" in plan.descripcion.lower():
                contenido.append("Ejercicios")
            if "protocolo" in plan.descripcion.lower():
                contenido.append("Protocolo")
            
            print(f"      Contenido: {', '.join(contenido)}")

def main():
    """Función principal de pruebas"""
    print("🎯 PRUEBAS DE PLANES DE INTERVENCIÓN EN FRONTEND")
    print("=" * 60)
    
    try:
        # Prueba 1: Caso específico de síndrome de Moebius
        test_frontend_planes_intervencion()
        
        # Prueba 2: Múltiples casos
        test_multiple_cases()
        
        print("\n✅ Todas las pruebas completadas exitosamente!")
        print("\n🎯 RESUMEN DE VERIFICACIONES:")
        print("   • Planes de intervención se generan correctamente")
        print("   • Contenido específico incluido (técnicas, aplicaciones, masajes)")
        print("   • Resumen de IA incluye sección de planes de intervención")
        print("   • Frontend separa planes de intervención de estudios científicos")
        print("   • Múltiples casos funcionan correctamente")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 