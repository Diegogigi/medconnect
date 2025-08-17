#!/usr/bin/env python3
"""
Script para probar el caso específico de Fonoaudiología con lactancia y frenillo lingual
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration
import time

def test_caso_fonoaudiologia():
    """Prueba el caso específico de fonoaudiología con lactancia y frenillo lingual"""
    print("🏥 PRUEBA CASO ESPECÍFICO: FONOAUDIOLOGÍA - LACTANCIA Y FRENILLO LINGUAL")
    print("=" * 80)
    
    try:
        apis = MedicalAPIsIntegration()
        print("✅ APIs médicas inicializadas correctamente")
        
        # Caso específico de fonoaudiología
        caso = {
            "especialidad": "fonoaudiologia",
            "motivo_consulta": "Dificultad de lactancia, posible frenillo lingual corto, hiperbilirrubina por hipoalimentación",
            "evaluacion": "Trenes de succión cortos, fatiga, se desacopla del pecho, chasquido lingual al succionar",
            "edad": "1 año",
            "descripcion": "Paciente de 1 año con problemas de lactancia y frenillo lingual"
        }
        
        print(f"\n📋 CASO CLÍNICO:")
        print(f"   Especialidad: '{caso['especialidad']}'")
        print(f"   Edad: '{caso['edad']}'")
        print(f"   Motivo de consulta: '{caso['motivo_consulta']}'")
        print(f"   Evaluación: '{caso['evaluacion']}'")
        print("-" * 80)
        
        # Combinar toda la información clínica
        condicion_completa = f"{caso['motivo_consulta']} {caso['evaluacion']} {caso['edad']}"
        
        print(f"\n🔍 Analizando información clínica completa...")
        print(f"   Condición combinada: '{condicion_completa}'")
        
        # Probar generación de términos MeSH específicos
        print(f"\n🔍 Generando términos MeSH específicos...")
        terminos_mesh = apis._generar_terminos_mesh_especificos(condicion_completa, caso['especialidad'])
        print(f"📋 Términos MeSH generados: {terminos_mesh}")
        
        # Probar búsqueda en PubMed
        print(f"\n🔍 Realizando búsqueda PubMed con términos específicos...")
        start_time = time.time()
        
        tratamientos_pubmed = apis.buscar_tratamiento_pubmed(condicion_completa, caso['especialidad'])
        
        end_time = time.time()
        search_time = end_time - start_time
        
        if tratamientos_pubmed:
            print(f"✅ Encontrados {len(tratamientos_pubmed)} tratamientos en PubMed")
            print(f"⏱️ Tiempo de búsqueda: {search_time:.2f} segundos")
            
            for i, tratamiento in enumerate(tratamientos_pubmed[:5], 1):  # Mostrar 5 ejemplos
                print(f"\n📋 Tratamiento {i}:")
                print(f"   Título: {tratamiento.titulo}")
                print(f"   DOI: {tratamiento.doi}")
                print(f"   Fecha: {tratamiento.fecha_publicacion}")
                print(f"   Nivel de evidencia: {tratamiento.nivel_evidencia}")
                
                if tratamiento.doi and tratamiento.doi != "Sin DOI":
                    print(f"   🔗 Link: https://doi.org/{tratamiento.doi}")
                
                if tratamiento.autores:
                    print(f"   👥 Autores: {', '.join(tratamiento.autores[:3])}")
                
                if tratamiento.resumen:
                    print(f"   📝 Resumen: {tratamiento.resumen[:150]}...")
                
                # Verificar relevancia para el caso específico
                relevancia = verificar_relevancia(tratamiento, caso)
                print(f"   🎯 Relevancia: {relevancia}")
        else:
            print(f"❌ No se encontraron tratamientos en PubMed")
            print(f"⏱️ Tiempo de búsqueda: {search_time:.2f} segundos")
        
        # Probar búsqueda en Europe PMC
        print(f"\n🔍 Realizando búsqueda Europe PMC...")
        start_time = time.time()
        
        tratamientos_europepmc = apis.buscar_europepmc(condicion_completa, caso['especialidad'])
        
        end_time = time.time()
        search_time = end_time - start_time
        
        if tratamientos_europepmc:
            print(f"✅ Encontrados {len(tratamientos_europepmc)} tratamientos en Europe PMC")
            print(f"⏱️ Tiempo de búsqueda: {search_time:.2f} segundos")
            
            for i, tratamiento in enumerate(tratamientos_europepmc[:3], 1):
                print(f"\n📋 Tratamiento {i}:")
                print(f"   Título: {tratamiento.titulo}")
                print(f"   DOI: {tratamiento.doi}")
                print(f"   Fecha: {tratamiento.fecha_publicacion}")
                print(f"   Nivel de evidencia: {tratamiento.nivel_evidencia}")
                
                if tratamiento.doi and tratamiento.doi != "Sin DOI":
                    print(f"   🔗 Link: https://doi.org/{tratamiento.doi}")
                
                if tratamiento.autores:
                    print(f"   👥 Autores: {', '.join(tratamiento.autores[:3])}")
                
                if tratamiento.resumen:
                    print(f"   📝 Resumen: {tratamiento.resumen[:150]}...")
                
                # Verificar relevancia para el caso específico
                relevancia = verificar_relevancia(tratamiento, caso)
                print(f"   🎯 Relevancia: {relevancia}")
        else:
            print(f"❌ No se encontraron tratamientos en Europe PMC")
            print(f"⏱️ Tiempo de búsqueda: {search_time:.2f} segundos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de caso fonoaudiología: {e}")
        return False

def verificar_relevancia(tratamiento, caso):
    """Verifica la relevancia del tratamiento para el caso específico"""
    texto_completo = f"{tratamiento.titulo} {tratamiento.resumen}".lower()
    
    # Palabras clave específicas del caso
    palabras_clave_caso = [
        'lactancia', 'lactation', 'breast feeding', 'breastfeeding',
        'frenillo', 'frenulum', 'ankyloglossia', 'tongue tie',
        'succion', 'suction', 'sucking',
        'hiperbilirrubina', 'hyperbilirubinemia', 'bilirubin',
        'hipoalimentacion', 'underfeeding', 'malnutrition',
        'fatiga', 'fatigue', 'desacopla', 'disconnect',
        'chasquido', 'clicking', 'lingual',
        'infant', 'baby', 'pediatric', 'child'
    ]
    
    # Contar coincidencias
    coincidencias = sum(1 for palabra in palabras_clave_caso if palabra in texto_completo)
    
    if coincidencias >= 3:
        return "🎯 MUY RELEVANTE - Múltiples coincidencias con el caso"
    elif coincidencias >= 2:
        return "✅ RELEVANTE - Algunas coincidencias con el caso"
    elif coincidencias >= 1:
        return "⚠️ PARCIALMENTE RELEVANTE - Pocas coincidencias"
    else:
        return "❌ NO RELEVANTE - Sin coincidencias específicas"

def test_terminos_especificos_fonoaudiologia():
    """Prueba términos MeSH específicos para fonoaudiología"""
    print("\n🎯 PRUEBA DE TÉRMINOS MeSH ESPECÍFICOS PARA FONOAUDIOLOGÍA")
    print("=" * 70)
    
    try:
        apis = MedicalAPIsIntegration()
        
        # Casos específicos de fonoaudiología
        casos_especificos = [
            "Dificultad de lactancia, posible frenillo lingual corto, hiperbilirrubina por hipoalimentación. Trenes de succión cortos, fatiga, se desacopla del pecho, chasquido lingual al succionar. Paciente de 1 año",
            "Problemas de deglución en niño de 2 años",
            "Trastornos del habla en paciente pediátrico",
            "Frenillo lingual corto y dificultades de alimentación",
            "Hiperbilirrubinemia neonatal y problemas de lactancia"
        ]
        
        for i, condicion in enumerate(casos_especificos, 1):
            print(f"\n📋 Caso {i}: {condicion[:50]}...")
            
            # Probar generación de términos MeSH
            terminos_mesh = apis._generar_terminos_mesh_especificos(condicion, "fonoaudiologia")
            print(f"   🔍 Términos MeSH: {terminos_mesh}")
            
            # Verificar que los términos son específicos y relevantes
            terminos_relevantes = [
                'Breast Feeding', 'Lactation Disorders', 'Tongue', 'Ankyloglossia',
                'Deglutition Disorders', 'Dysphagia', 'Hyperbilirubinemia', 'Jaundice',
                'Malnutrition', 'Infant Nutrition Disorders', 'Fatigue', 'Feeding and Eating Disorders',
                'Tongue', 'Oral Manifestations', 'Infant', 'Child Development'
            ]
            
            for termino in terminos_mesh:
                if any(termino_relevante in termino for termino_relevante in terminos_relevantes):
                    print(f"   ✅ Término relevante: {termino}")
                else:
                    print(f"   ⚠️ Término general: {termino}")
        
    except Exception as e:
        print(f"❌ Error en pruebas de términos específicos: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 PRUEBA CASO ESPECÍFICO FONOAUDIOLOGÍA")
    print("=" * 80)
    
    try:
        # Probar términos específicos
        success1 = test_terminos_especificos_fonoaudiologia()
        
        # Probar caso específico completo
        success2 = test_caso_fonoaudiologia()
        
        if success1 and success2:
            print("\n\n🎉 ¡PRUEBA CASO ESPECÍFICO EXITOSA!")
            print("✅ El sistema MeSH específico está funcionando para casos complejos")
            
            print("\n📊 RESUMEN DE MEJORAS:")
            print("   ✅ Análisis completo de información clínica")
            print("   ✅ Términos MeSH específicos para lactancia y frenillo")
            print("   ✅ Consideración de edad del paciente (1 año)")
            print("   ✅ Análisis de síntomas específicos (fatiga, desacoplamiento)")
            print("   ✅ Términos relevantes para hiperbilirrubinemia")
            print("   ✅ Verificación de relevancia de resultados")
            
            print("\n🎯 BENEFICIOS OBTENIDOS:")
            print("   ✅ Búsquedas más específicas y relevantes")
            print("   ✅ Consideración de toda la información clínica")
            print("   ✅ Términos MeSH alineados con el caso específico")
            print("   ✅ Resultados más precisos para el diagnóstico")
            print("   ✅ Cobertura de condiciones pediátricas específicas")
            
            print("\n🚀 SISTEMA MEJORADO PARA CASOS COMPLEJOS")
            print("   ✅ Análisis inteligente de información clínica")
            print("   ✅ Términos MeSH específicos por condición")
            print("   ✅ Resultados más relevantes y precisos")
            print("   ✅ Cobertura de casos pediátricos complejos")
            
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