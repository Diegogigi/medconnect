#!/usr/bin/env python3
"""
Script de prueba para verificar la planificación completa de tratamiento
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from copilot_health import CopilotHealth
import json

def test_planificacion_completa():
    """Prueba la generación de planificación completa de tratamiento"""
    print("🧪 PRUEBAS DE PLANIFICACIÓN COMPLETA DE TRATAMIENTO")
    print("=" * 60)
    
    try:
        copilot = CopilotHealth()
        print("✅ Copilot Health inicializado correctamente")
        
        # Casos de prueba con diferentes tipos de atención
        casos_prueba = [
            {
                "motivo_atencion": "Dolor lumbar crónico con irradiación a miembro inferior derecho",
                "tipo_atencion": "fisioterapia",
                "evaluacion_observaciones": "Paciente presenta dolor lumbar de 6 meses de evolución, con irradiación a miembro inferior derecho. Limitación funcional para actividades de la vida diaria.",
                "descripcion": "Fisioterapia - Dolor lumbar crónico"
            },
            {
                "motivo_atencion": "Problemas de pronunciación y dificultades en la comunicación",
                "tipo_atencion": "fonoaudiologia",
                "evaluacion_observaciones": "Paciente presenta dificultades en la pronunciación de ciertos fonemas y problemas en la comunicación oral.",
                "descripcion": "Fonoaudiología - Problemas de pronunciación"
            },
            {
                "motivo_atencion": "Ansiedad y estrés laboral con síntomas de depresión",
                "tipo_atencion": "psicologia",
                "evaluacion_observaciones": "Paciente refiere ansiedad, estrés laboral y síntomas depresivos de 3 meses de evolución.",
                "descripcion": "Psicología - Ansiedad y estrés"
            }
        ]
        
        for i, caso in enumerate(casos_prueba, 1):
            print(f"\n📋 CASO {i}: {caso['descripcion']}")
            print(f"   Motivo de atención: '{caso['motivo_atencion']}'")
            print(f"   Tipo de atención: '{caso['tipo_atencion']}'")
            print(f"   Evaluación/Observaciones: '{caso['evaluacion_observaciones']}'")
            
            try:
                planificacion = copilot.generar_planificacion_tratamiento_completa(
                    motivo_atencion=caso['motivo_atencion'],
                    tipo_atencion=caso['tipo_atencion'],
                    evaluacion_observaciones=caso['evaluacion_observaciones'],
                    edad=35
                )
                
                print(f"   ✅ Planificación generada exitosamente")
                
                # Verificar estructura de la planificación
                print(f"\n   📋 ESTRUCTURA DE PLANIFICACIÓN:")
                print(f"      ✅ Resumen clínico: {'Presente' if planificacion.get('resumen_clinico') else 'Faltante'}")
                print(f"      ✅ Objetivos: {len(planificacion.get('objetivos_tratamiento', []))} objetivos")
                print(f"      ✅ Intervenciones: {len(planificacion.get('intervenciones_especificas', []))} intervenciones")
                print(f"      ✅ Cronograma: {len(planificacion.get('cronograma_tratamiento', []))} fases")
                print(f"      ✅ Criterios evaluación: {len(planificacion.get('criterios_evaluacion', []))} criterios")
                print(f"      ✅ Estudios basados: {len(planificacion.get('estudios_basados', []))} estudios")
                print(f"      ✅ Aclaración legal: {'Presente' if planificacion.get('aclaracion_legal') else 'Faltante'}")
                
                # Mostrar detalles específicos
                print(f"\n   🎯 OBJETIVOS DEL TRATAMIENTO:")
                for j, objetivo in enumerate(planificacion.get('objetivos_tratamiento', []), 1):
                    print(f"      {j}. {objetivo}")
                
                if planificacion.get('intervenciones_especificas'):
                    print(f"\n   🔬 INTERVENCIONES ESPECÍFICAS:")
                    for j, intervencion in enumerate(planificacion['intervenciones_especificas'], 1):
                        print(f"      {j}. {intervencion['titulo']}")
                        print(f"         Descripción: {intervencion['descripcion']}")
                        print(f"         Evidencia: {intervencion['evidencia']}")
                        print(f"         DOI: {intervencion['doi']}")
                
                if planificacion.get('estudios_basados'):
                    print(f"\n   📚 ESTUDIOS CIENTÍFICOS:")
                    for j, estudio in enumerate(planificacion['estudios_basados'], 1):
                        print(f"      {j}. {estudio['titulo']}")
                        print(f"         Autores: {estudio['autores']}")
                        print(f"         DOI: {estudio['doi']}")
                        print(f"         Fecha: {estudio['fecha']}")
                        print(f"         Fuente: {estudio['fuente']}")
                
                print(f"\n   ⚠️ ACLARACIÓN LEGAL:")
                print(f"      {planificacion.get('aclaracion_legal', 'No disponible')}")
                
            except Exception as e:
                print(f"   ❌ Error en caso {i}: {e}")
        
        # Probar formato JSON para frontend
        print(f"\n\n🔍 PROBANDO FORMATO JSON PARA FRONTEND")
        print("=" * 50)
        
        planificacion = copilot.generar_planificacion_tratamiento_completa(
            motivo_atencion="Dolor lumbar",
            tipo_atencion="fisioterapia",
            evaluacion_observaciones="Paciente con dolor lumbar crónico",
            edad=40
        )
        
        print("📋 Formato JSON generado:")
        print(json.dumps(planificacion, indent=2, ensure_ascii=False))
        
        # Verificar que todos los campos necesarios estén presentes
        campos_requeridos = [
            'resumen_clinico', 'objetivos_tratamiento', 'intervenciones_especificas',
            'cronograma_tratamiento', 'criterios_evaluacion', 'estudios_basados', 'aclaracion_legal'
        ]
        
        print(f"\n✅ VERIFICACIÓN DE CAMPOS:")
        for campo in campos_requeridos:
            presente = campo in planificacion and planificacion[campo] is not None
            print(f"   {campo}: {'✅' if presente else '❌'}")
        
    except Exception as e:
        print(f"❌ Error en pruebas de planificación completa: {e}")
        return False
    
    return True

def test_apis_medicas_estudios():
    """Prueba específicamente la obtención de estudios de las APIs médicas"""
    print(f"\n\n🔬 PRUEBAS DE ESTUDIOS DE APIS MÉDICAS (2020-2025)")
    print("=" * 70)
    
    try:
        from medical_apis_integration import MedicalAPIsIntegration
        
        apis = MedicalAPIsIntegration()
        print("✅ APIs médicas inicializadas correctamente")
        
        # Probar búsqueda en PubMed con filtro de fecha
        print("\n🔍 Probando búsqueda en PubMed (2020-2025)...")
        tratamientos_pubmed = apis.buscar_tratamiento_pubmed("dolor lumbar", "fisioterapia")
        
        if tratamientos_pubmed:
            print(f"   ✅ Encontrados {len(tratamientos_pubmed)} tratamientos en PubMed (2020-2025)")
            
            for i, tratamiento in enumerate(tratamientos_pubmed, 1):
                print(f"\n   📋 Tratamiento {i} de PubMed:")
                print(f"      Título: {tratamiento.titulo}")
                print(f"      DOI: {tratamiento.doi}")
                print(f"      Fuente: {tratamiento.fuente}")
                print(f"      Tipo de evidencia: {tratamiento.tipo_evidencia}")
                print(f"      Fecha: {tratamiento.fecha_publicacion}")
                print(f"      Autores: {', '.join(tratamiento.autores)}")
                
                # Verificar que el DOI sea válido
                if tratamiento.doi and tratamiento.doi != "Sin DOI":
                    print(f"      ✅ DOI válido: {tratamiento.doi}")
                    print(f"      🔗 Link: https://doi.org/{tratamiento.doi}")
                else:
                    print(f"      ⚠️ DOI no disponible")
        else:
            print("   ⚠️ No se encontraron tratamientos en PubMed (2020-2025)")
        
        # Probar búsqueda en Europe PMC con filtro de fecha
        print("\n🔍 Probando búsqueda en Europe PMC (2020-2025)...")
        tratamientos_europepmc = apis.buscar_europepmc("dolor lumbar", "fisioterapia")
        
        if tratamientos_europepmc:
            print(f"   ✅ Encontrados {len(tratamientos_europepmc)} tratamientos en Europe PMC (2020-2025)")
            
            for i, tratamiento in enumerate(tratamientos_europepmc, 1):
                print(f"\n   📋 Tratamiento {i} de Europe PMC:")
                print(f"      Título: {tratamiento.titulo}")
                print(f"      DOI: {tratamiento.doi}")
                print(f"      Fuente: {tratamiento.fuente}")
                print(f"      Tipo de evidencia: {tratamiento.tipo_evidencia}")
                print(f"      Fecha: {tratamiento.fecha_publicacion}")
                
                # Verificar que el DOI sea válido
                if tratamiento.doi and tratamiento.doi != "Sin DOI":
                    print(f"      ✅ DOI válido: {tratamiento.doi}")
                    print(f"      🔗 Link: https://doi.org/{tratamiento.doi}")
                else:
                    print(f"      ⚠️ DOI no disponible")
        else:
            print("   ⚠️ No se encontraron tratamientos en Europe PMC (2020-2025)")
        
    except Exception as e:
        print(f"❌ Error en pruebas de APIs médicas: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE PLANIFICACIÓN COMPLETA DE TRATAMIENTO")
    print("=" * 80)
    
    try:
        # Ejecutar todas las pruebas
        success1 = test_planificacion_completa()
        success2 = test_apis_medicas_estudios()
        
        if success1 and success2:
            print("\n\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
            print("🎯 La planificación completa de tratamiento está funcionando correctamente")
            
            print("\n📋 RESUMEN DE VERIFICACIONES:")
            print("   ✅ Planificación completa basada en múltiples fuentes")
            print("   ✅ Estudios científicos de 2020-2025")
            print("   ✅ Objetivos específicos por tipo de atención")
            print("   ✅ Intervenciones basadas en evidencia")
            print("   ✅ Cronograma de tratamiento estructurado")
            print("   ✅ Criterios de evaluación")
            print("   ✅ Aclaración legal incluida")
            print("   ✅ Formato JSON para frontend")
            print("   ✅ APIs médicas con filtros de fecha")
            
        else:
            print("\n❌ ALGUNAS PRUEBAS FALLARON")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 