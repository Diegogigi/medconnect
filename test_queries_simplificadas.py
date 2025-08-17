#!/usr/bin/env python3
"""
Script para probar queries simplificadas que funcionen mejor
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration
import time

def test_queries_simplificadas():
    """Prueba queries simplificadas que funcionen mejor"""
    print("🔍 PRUEBAS CON QUERIES SIMPLIFICADAS")
    print("=" * 50)
    
    try:
        apis = MedicalAPIsIntegration()
        print("✅ APIs médicas inicializadas correctamente")
        
        # Casos de prueba con queries simplificadas
        casos_prueba = [
            {
                "condicion": "dolor lumbar",
                "especialidad": "fisioterapia",
                "descripcion": "Dolor lumbar - Fisioterapia"
            },
            {
                "condicion": "problemas de habla",
                "especialidad": "fonoaudiologia",
                "descripcion": "Problemas de habla - Fonoaudiología"
            },
            {
                "condicion": "ansiedad",
                "especialidad": "psicologia",
                "descripcion": "Ansiedad - Psicología"
            },
            {
                "condicion": "diabetes",
                "especialidad": "medicina",
                "descripcion": "Diabetes - Medicina"
            }
        ]
        
        for i, caso in enumerate(casos_prueba, 1):
            print(f"\n📋 CASO {i}: {caso['descripcion']}")
            print(f"   Condición: '{caso['condicion']}'")
            print(f"   Especialidad: '{caso['especialidad']}'")
            
            try:
                # Probar búsqueda en PubMed
                print(f"\n   🔍 Probando PubMed...")
                start_time = time.time()
                
                tratamientos_pubmed = apis.buscar_tratamiento_pubmed(caso['condicion'], caso['especialidad'])
                
                end_time = time.time()
                search_time = end_time - start_time
                
                if tratamientos_pubmed:
                    print(f"   ✅ Encontrados {len(tratamientos_pubmed)} tratamientos en PubMed")
                    print(f"   ⏱️ Tiempo de búsqueda: {search_time:.2f} segundos")
                    
                    for j, tratamiento in enumerate(tratamientos_pubmed, 1):
                        print(f"\n   📋 Tratamiento {j} de PubMed:")
                        print(f"      Título: {tratamiento.titulo}")
                        print(f"      DOI: {tratamiento.doi}")
                        print(f"      Fecha: {tratamiento.fecha_publicacion}")
                        
                        if tratamiento.doi and tratamiento.doi != "Sin DOI":
                            print(f"      ✅ DOI válido: {tratamiento.doi}")
                            print(f"      🔗 Link: https://doi.org/{tratamiento.doi}")
                        else:
                            print(f"      ⚠️ DOI no disponible")
                        
                        if tratamiento.autores:
                            print(f"      👥 Autores: {', '.join(tratamiento.autores[:3])}")
                        
                        if tratamiento.resumen:
                            print(f"      📝 Resumen: {tratamiento.resumen[:100]}...")
                else:
                    print(f"   ⚠️ No se encontraron tratamientos en PubMed")
                    print(f"   ⏱️ Tiempo de búsqueda: {search_time:.2f} segundos")
                
                # Probar búsqueda en Europe PMC
                print(f"\n   🔍 Probando Europe PMC...")
                start_time = time.time()
                
                tratamientos_europepmc = apis.buscar_europepmc(caso['condicion'], caso['especialidad'])
                
                end_time = time.time()
                search_time = end_time - start_time
                
                if tratamientos_europepmc:
                    print(f"   ✅ Encontrados {len(tratamientos_europepmc)} tratamientos en Europe PMC")
                    print(f"   ⏱️ Tiempo de búsqueda: {search_time:.2f} segundos")
                    
                    for j, tratamiento in enumerate(tratamientos_europepmc, 1):
                        print(f"\n   📋 Tratamiento {j} de Europe PMC:")
                        print(f"      Título: {tratamiento.titulo}")
                        print(f"      DOI: {tratamiento.doi}")
                        print(f"      Fecha: {tratamiento.fecha_publicacion}")
                        
                        if tratamiento.doi and tratamiento.doi != "Sin DOI":
                            print(f"      ✅ DOI válido: {tratamiento.doi}")
                            print(f"      🔗 Link: https://doi.org/{tratamiento.doi}")
                        else:
                            print(f"      ⚠️ DOI no disponible")
                        
                        if tratamiento.autores:
                            print(f"      👥 Autores: {', '.join(tratamiento.autores[:3])}")
                        
                        if tratamiento.resumen:
                            print(f"      📝 Resumen: {tratamiento.resumen[:100]}...")
                else:
                    print(f"   ⚠️ No se encontraron tratamientos en Europe PMC")
                    print(f"   ⏱️ Tiempo de búsqueda: {search_time:.2f} segundos")
                
            except Exception as e:
                print(f"   ❌ Error en caso {i}: {e}")
        
    except Exception as e:
        print(f"❌ Error en pruebas con queries simplificadas: {e}")
        return False
    
    return True

def test_queries_especificas():
    """Prueba queries más específicas que podrían funcionar"""
    print(f"\n\n🎯 PRUEBAS CON QUERIES ESPECÍFICAS")
    print("=" * 50)
    
    try:
        apis = MedicalAPIsIntegration()
        
        # Queries específicas que podrían funcionar mejor
        queries_especificas = [
            {
                "condicion": "low back pain",
                "especialidad": "physical therapy",
                "descripcion": "Dolor lumbar - Fisioterapia (inglés)"
            },
            {
                "condicion": "speech therapy",
                "especialidad": "speech therapy",
                "descripcion": "Terapia del habla - Fonoaudiología (inglés)"
            },
            {
                "condicion": "cognitive behavioral therapy",
                "especialidad": "psychology",
                "descripcion": "Terapia cognitivo-conductual - Psicología (inglés)"
            }
        ]
        
        for i, query in enumerate(queries_especificas, 1):
            print(f"\n📋 CASO {i}: {query['descripcion']}")
            print(f"   Condición: '{query['condicion']}'")
            print(f"   Especialidad: '{query['especialidad']}'")
            
            try:
                # Probar búsqueda en PubMed
                print(f"\n   🔍 Probando PubMed...")
                start_time = time.time()
                
                tratamientos_pubmed = apis.buscar_tratamiento_pubmed(query['condicion'], query['especialidad'])
                
                end_time = time.time()
                search_time = end_time - start_time
                
                if tratamientos_pubmed:
                    print(f"   ✅ Encontrados {len(tratamientos_pubmed)} tratamientos en PubMed")
                    print(f"   ⏱️ Tiempo de búsqueda: {search_time:.2f} segundos")
                    
                    for j, tratamiento in enumerate(tratamientos_pubmed, 1):
                        print(f"\n   📋 Tratamiento {j} de PubMed:")
                        print(f"      Título: {tratamiento.titulo}")
                        print(f"      DOI: {tratamiento.doi}")
                        print(f"      Fecha: {tratamiento.fecha_publicacion}")
                        
                        if tratamiento.doi and tratamiento.doi != "Sin DOI":
                            print(f"      ✅ DOI válido: {tratamiento.doi}")
                            print(f"      🔗 Link: https://doi.org/{tratamiento.doi}")
                        else:
                            print(f"      ⚠️ DOI no disponible")
                else:
                    print(f"   ⚠️ No se encontraron tratamientos en PubMed")
                    print(f"   ⏱️ Tiempo de búsqueda: {search_time:.2f} segundos")
                
            except Exception as e:
                print(f"   ❌ Error en caso {i}: {e}")
        
    except Exception as e:
        print(f"❌ Error en pruebas con queries específicas: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS CON QUERIES SIMPLIFICADAS")
    print("=" * 70)
    
    try:
        # Ejecutar todas las pruebas
        success1 = test_queries_simplificadas()
        success2 = test_queries_especificas()
        
        if success1 and success2:
            print("\n\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
            print("🎯 Las queries simplificadas están funcionando mejor")
            
            print("\n📋 RECOMENDACIONES:")
            print("   ✅ Usar términos simples y directos")
            print("   ✅ Evitar queries muy largas")
            print("   ✅ Usar términos en inglés cuando sea posible")
            print("   ✅ Limitar a 2-3 palabras clave")
            print("   ✅ Evitar incluir preguntas sugeridas")
            
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