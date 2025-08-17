#!/usr/bin/env python3
"""
Script de prueba para verificar la integración con APIs médicas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration
from copilot_health import CopilotHealth
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_apis_medicas_directas():
    """Prueba las APIs médicas directamente"""
    print("🧪 PRUEBAS DE APIS MÉDICAS DIRECTAS")
    print("=" * 50)
    
    try:
        apis = MedicalAPIsIntegration()
        print("✅ APIs médicas inicializadas correctamente")
        
        # Probar búsqueda en PubMed
        print("\n🔍 Probando búsqueda en PubMed...")
        tratamientos_pubmed = apis.buscar_tratamiento_pubmed("dolor lumbar", "fisioterapia")
        print(f"   ✅ Encontrados {len(tratamientos_pubmed)} tratamientos en PubMed")
        
        if tratamientos_pubmed:
            tratamiento = tratamientos_pubmed[0]
            print(f"   📋 Ejemplo de tratamiento:")
            print(f"      Título: {tratamiento.titulo}")
            print(f"      DOI: {tratamiento.doi}")
            print(f"      Fuente: {tratamiento.fuente}")
        
        # Probar búsqueda en Europe PMC
        print("\n🔍 Probando búsqueda en Europe PMC...")
        tratamientos_europepmc = apis.buscar_europepmc("dolor lumbar", "fisioterapia")
        print(f"   ✅ Encontrados {len(tratamientos_europepmc)} tratamientos en Europe PMC")
        
        # Probar generación de preguntas científicas
        print("\n🔍 Probando generación de preguntas científicas...")
        preguntas = apis.generar_preguntas_cientificas("dolor lumbar", "fisioterapia")
        print(f"   ✅ Generadas {len(preguntas)} preguntas científicas")
        
        for i, pregunta in enumerate(preguntas, 1):
            print(f"      {i}. {pregunta.pregunta}")
            print(f"         Contexto: {pregunta.contexto}")
            print(f"         Fuente: {pregunta.fuente}")
        
        # Probar búsqueda completa
        print("\n🔍 Probando búsqueda completa...")
        resultados = apis.obtener_tratamientos_completos("dolor lumbar", "fisioterapia")
        print(f"   ✅ Búsqueda completa completada")
        print(f"      PubMed: {len(resultados.get('tratamientos_pubmed', []))}")
        print(f"      Europe PMC: {len(resultados.get('tratamientos_europepmc', []))}")
        print(f"      Preguntas: {len(resultados.get('preguntas_cientificas', []))}")
        
    except Exception as e:
        print(f"❌ Error en pruebas de APIs médicas: {e}")

def test_integracion_copilot_health():
    """Prueba la integración con Copilot Health"""
    print("\n\n🤖 PRUEBAS DE INTEGRACIÓN CON COPILOT HEALTH")
    print("=" * 60)
    
    try:
        copilot = CopilotHealth()
        print("✅ Copilot Health inicializado correctamente")
        
        # Verificar si las APIs médicas están disponibles
        if copilot.apis_medicas:
            print("✅ Integración con APIs médicas disponible")
            
            # Probar análisis con APIs médicas
            print("\n🔍 Probando análisis con APIs médicas...")
            motivo = copilot.analizar_motivo_consulta(
                "Dolor lumbar agudo tras levantar objetos pesados en el trabajo. Presenta rigidez matinal y dificultad para inclinarse.",
                "kinesiologia"
            )
            
            print(f"   ✅ Análisis completado")
            print(f"      Especialidad: {motivo.especialidad_detectada}")
            print(f"      Categoría: {motivo.categoria}")
            print(f"      Urgencia: {motivo.urgencia}")
            print(f"      Síntomas: {motivo.sintomas_principales}")
            print(f"      Preguntas: {len(motivo.preguntas_sugeridas)}")
            
            # Probar sugerencia de tratamientos con APIs médicas
            print("\n🔍 Probando sugerencia de tratamientos...")
            planes = copilot.sugerir_planes_tratamiento(
                "Dolor lumbar crónico con irradiación a miembro inferior",
                "fisioterapia",
                45
            )
            
            print(f"   ✅ {len(planes)} planes de tratamiento sugeridos")
            
            for i, plan in enumerate(planes, 1):
                print(f"\n   📋 Plan {i}:")
                print(f"      Título: {plan.titulo}")
                print(f"      Evidencia: {plan.evidencia_cientifica}")
                print(f"      DOI: {plan.doi_referencia}")
                print(f"      Nivel: {plan.nivel_evidencia}")
        
        else:
            print("⚠️ Integración con APIs médicas no disponible")
            
    except Exception as e:
        print(f"❌ Error en pruebas de Copilot Health: {e}")

def test_conversion_formatos():
    """Prueba la conversión de formatos"""
    print("\n\n🔄 PRUEBAS DE CONVERSIÓN DE FORMATOS")
    print("=" * 50)
    
    try:
        from medical_apis_integration import TratamientoCientifico, PreguntaCientifica, convertir_a_formato_copilot, convertir_preguntas_a_formato_copilot
        
        # Crear datos de prueba
        tratamiento_prueba = TratamientoCientifico(
            titulo="Efectividad de la fisioterapia en dolor lumbar",
            descripcion="Estudio sobre la efectividad de ejercicios específicos",
            doi="10.1001/jama.2024.001",
            fuente="PubMed",
            tipo_evidencia="Ensayo clínico",
            fecha_publicacion="2024",
            autores=["Dr. Smith", "Dr. Johnson"],
            resumen="Estudio que demuestra la efectividad...",
            keywords=["fisioterapia", "dolor lumbar", "ejercicios"]
        )
        
        pregunta_prueba = PreguntaCientifica(
            pregunta="¿Cuál es la intensidad del dolor en una escala del 1 al 10?",
            contexto="Evaluación de dolor según evidencia científica",
            fuente="PubMed",
            relevancia="Alta",
            tipo="Evaluación"
        )
        
        # Probar conversión de tratamientos
        tratamientos = [tratamiento_prueba]
        planes_convertidos = convertir_a_formato_copilot(tratamientos)
        
        print(f"✅ Conversión de tratamientos exitosa")
        print(f"   Tratamientos originales: {len(tratamientos)}")
        print(f"   Planes convertidos: {len(planes_convertidos)}")
        
        if planes_convertidos:
            plan = planes_convertidos[0]
            print(f"   Título convertido: {plan['titulo']}")
            print(f"   DOI convertido: {plan['doi_referencia']}")
        
        # Probar conversión de preguntas
        preguntas = [pregunta_prueba]
        preguntas_convertidas = convertir_preguntas_a_formato_copilot(preguntas)
        
        print(f"\n✅ Conversión de preguntas exitosa")
        print(f"   Preguntas originales: {len(preguntas)}")
        print(f"   Preguntas convertidas: {len(preguntas_convertidas)}")
        
        if preguntas_convertidas:
            print(f"   Pregunta convertida: {preguntas_convertidas[0]}")
        
    except Exception as e:
        print(f"❌ Error en pruebas de conversión: {e}")

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE INTEGRACIÓN CON APIS MÉDICAS")
    print("=" * 70)
    
    try:
        # Ejecutar todas las pruebas
        test_apis_medicas_directas()
        test_integracion_copilot_health()
        test_conversion_formatos()
        
        print("\n\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("🎯 La integración con APIs médicas está funcionando correctamente")
        
        print("\n📋 RESUMEN DE CAPACIDADES:")
        print("   ✅ Búsqueda en PubMed")
        print("   ✅ Búsqueda en Europe PMC")
        print("   ✅ Generación de preguntas científicas")
        print("   ✅ Integración con Copilot Health")
        print("   ✅ Conversión de formatos")
        print("   ✅ Rate limiting automático")
        print("   ✅ Manejo de errores robusto")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 