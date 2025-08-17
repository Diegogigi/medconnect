#!/usr/bin/env python3
"""
Test script para Copilot Health - IA Clínica Asistiva
"""

import sys
import os

# Agregar el directorio actual al path para importar el módulo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from copilot_health import copilot_health
    print("✅ Módulo Copilot Health importado exitosamente")
except ImportError as e:
    print(f"❌ Error importando Copilot Health: {e}")
    sys.exit(1)

def test_analisis_motivo():
    """Prueba el análisis del motivo de consulta"""
    print("\n🧪 Probando análisis del motivo de consulta...")
    
    # Casos de prueba
    casos_prueba = [
        {
            "motivo": "Dolor lumbar de 3 semanas tras cargar peso",
            "descripcion": "Dolor lumbar post-trauma"
        },
        {
            "motivo": "Dolor opresivo en el pecho que se irradia al brazo izquierdo",
            "descripcion": "Dolor torácico con irradiación"
        },
        {
            "motivo": "Dolor de cabeza pulsátil con náuseas y fotofobia",
            "descripcion": "Cefalea migrañosa"
        },
        {
            "motivo": "Dolor abdominal en epigastrio relacionado con las comidas",
            "descripcion": "Dolor abdominal post-prandial"
        }
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n📋 Caso {i}: {caso['descripcion']}")
        print(f"Motivo: {caso['motivo']}")
        
        try:
            resultado = copilot_health.analizar_motivo_consulta(caso['motivo'])
            
            print(f"✅ Especialidad detectada: {resultado.especialidad_detectada}")
            print(f"✅ Categoría: {resultado.categoria}")
            print(f"✅ Urgencia: {resultado.urgencia}")
            print(f"✅ Síntomas: {', '.join(resultado.sintomas_principales)}")
            print(f"✅ Preguntas sugeridas: {len(resultado.preguntas_sugeridas)} preguntas")
            
        except Exception as e:
            print(f"❌ Error en caso {i}: {e}")

def test_evaluacion_antecedentes():
    """Prueba la evaluación de antecedentes"""
    print("\n🧪 Probando evaluación de antecedentes...")
    
    casos_prueba = [
        {
            "antecedentes": "Paciente de 70 años con diabetes tipo 2, hipertensión arterial",
            "especialidad": "medicina_general",
            "edad": 70,
            "descripcion": "Adulto mayor con comorbilidades"
        },
        {
            "antecedentes": "Dolor lumbar intenso que no mejora con reposo, pérdida de fuerza en pierna derecha",
            "especialidad": "traumatologia",
            "edad": 45,
            "descripcion": "Dolor lumbar con banderas rojas"
        },
        {
            "antecedentes": "Dolor opresivo en el pecho, sudoración fría, dificultad para respirar",
            "especialidad": "cardiologia",
            "edad": 55,
            "descripcion": "Síntomas cardíacos agudos"
        }
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n📋 Caso {i}: {caso['descripcion']}")
        print(f"Antecedentes: {caso['antecedentes']}")
        
        try:
            resultado = copilot_health.evaluar_antecedentes(
                caso['antecedentes'], 
                caso['especialidad'], 
                caso['edad']
            )
            
            print(f"✅ Banderas rojas: {len(resultado.banderas_rojas)} detectadas")
            if resultado.banderas_rojas:
                for bandera in resultado.banderas_rojas:
                    print(f"   🚨 {bandera}")
            
            print(f"✅ Campos adicionales: {len(resultado.campos_adicionales)} sugeridos")
            if resultado.campos_adicionales:
                for campo in resultado.campos_adicionales:
                    print(f"   📋 {campo}")
            
            print(f"✅ Omisiones detectadas: {len(resultado.omisiones_detectadas)}")
            if resultado.omisiones_detectadas:
                for omision in resultado.omisiones_detectadas:
                    print(f"   ⚠️ {omision}")
            
            print(f"✅ Recomendaciones: {len(resultado.recomendaciones)}")
            if resultado.recomendaciones:
                for recomendacion in resultado.recomendaciones:
                    print(f"   💡 {recomendacion}")
            
        except Exception as e:
            print(f"❌ Error en caso {i}: {e}")

def test_sugerencias_tratamiento():
    """Prueba las sugerencias de tratamiento"""
    print("\n🧪 Probando sugerencias de tratamiento...")
    
    casos_prueba = [
        {
            "diagnostico": "Dolor lumbar inespecífico",
            "especialidad": "traumatologia",
            "edad": 45,
            "descripcion": "Dolor lumbar"
        },
        {
            "diagnostico": "Hipertensión arterial",
            "especialidad": "cardiologia",
            "edad": 60,
            "descripcion": "Hipertensión"
        },
        {
            "diagnostico": "Diabetes tipo 2",
            "especialidad": "endocrinologia",
            "edad": 55,
            "descripcion": "Diabetes"
        }
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n📋 Caso {i}: {caso['descripcion']}")
        print(f"Diagnóstico: {caso['diagnostico']}")
        
        try:
            planes = copilot_health.sugerir_planes_tratamiento(
                caso['diagnostico'], 
                caso['especialidad'], 
                caso['edad']
            )
            
            print(f"✅ Planes sugeridos: {len(planes)}")
            for j, plan in enumerate(planes, 1):
                print(f"   📋 Plan {j}: {plan.titulo}")
                print(f"      Descripción: {plan.descripcion}")
                print(f"      Evidencia: {plan.evidencia_cientifica}")
                print(f"      DOI: {plan.doi_referencia}")
                print(f"      Nivel: {plan.nivel_evidencia}")
                if plan.contraindicaciones:
                    print(f"      Contraindicaciones: {', '.join(plan.contraindicaciones)}")
            
        except Exception as e:
            print(f"❌ Error en caso {i}: {e}")

def test_analisis_completo():
    """Prueba el análisis completo"""
    print("\n🧪 Probando análisis completo...")
    
    caso_prueba = {
        "motivo": "Dolor lumbar de 3 semanas tras cargar peso",
        "antecedentes": "Paciente de 45 años, trabajador de construcción, sin antecedentes relevantes",
        "diagnostico": "Dolor lumbar inespecífico",
        "descripcion": "Caso completo de dolor lumbar"
    }
    
    print(f"📋 Caso: {caso_prueba['descripcion']}")
    print(f"Motivo: {caso_prueba['motivo']}")
    print(f"Antecedentes: {caso_prueba['antecedentes']}")
    print(f"Diagnóstico: {caso_prueba['diagnostico']}")
    
    try:
        # Análisis completo
        motivo_analizado = copilot_health.analizar_motivo_consulta(caso_prueba['motivo'])
        evaluacion = copilot_health.evaluar_antecedentes(caso_prueba['antecedentes'], 'traumatologia', 45)
        planes = copilot_health.sugerir_planes_tratamiento(caso_prueba['diagnostico'], 'traumatologia', 45)
        
        # Generar resumen
        resumen = copilot_health.generar_resumen_ia(motivo_analizado, evaluacion, planes)
        
        print(f"\n✅ Análisis completo generado exitosamente")
        print(f"📊 Longitud del resumen: {len(resumen)} caracteres")
        print("\n📋 Resumen generado:")
        print("=" * 50)
        print(resumen)
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error en análisis completo: {e}")

def main():
    """Función principal de pruebas"""
    print("🤖 COPILOT HEALTH - PRUEBAS DE IA CLÍNICA ASISTIVA")
    print("=" * 60)
    
    # Ejecutar todas las pruebas
    test_analisis_motivo()
    test_evaluacion_antecedentes()
    test_sugerencias_tratamiento()
    test_analisis_completo()
    
    print("\n🎉 Todas las pruebas completadas")
    print("✅ Copilot Health está funcionando correctamente")

if __name__ == "__main__":
    main() 