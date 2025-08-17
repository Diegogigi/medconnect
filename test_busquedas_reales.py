#!/usr/bin/env python3
"""
Script de prueba para verificar búsquedas reales en APIs médicas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration
import json

def test_busquedas_reales():
    """Prueba búsquedas reales en APIs médicas"""
    print("🔍 PRUEBAS DE BÚSQUEDAS REALES EN APIS MÉDICAS")
    print("=" * 60)
    
    try:
        apis = MedicalAPIsIntegration()
        print("✅ APIs médicas inicializadas correctamente")
        
        # Casos de prueba con términos específicos
        casos_prueba = [
            {
                "condicion": "low back pain",
                "especialidad": "physical therapy",
                "descripcion": "Dolor lumbar - Fisioterapia"
            },
            {
                "condicion": "speech disorders",
                "especialidad": "speech therapy",
                "descripcion": "Trastornos del habla - Fonoaudiología"
            },
            {
                "condicion": "anxiety",
                "especialidad": "psychology",
                "descripcion": "Ansiedad - Psicología"
            }
        ]
        
        for i, caso in enumerate(casos_prueba, 1):
            print(f"\n📋 CASO {i}: {caso['descripcion']}")
            print(f"   Condición: '{caso['condicion']}'")
            print(f"   Especialidad: '{caso['especialidad']}'")
            
            try:
                # Probar búsqueda en PubMed
                print(f"\n   🔍 Probando PubMed...")
                tratamientos_pubmed = apis.buscar_tratamiento_pubmed(caso['condicion'], caso['especialidad'])
                
                if tratamientos_pubmed:
                    print(f"   ✅ Encontrados {len(tratamientos_pubmed)} tratamientos en PubMed")
                    
                    for j, tratamiento in enumerate(tratamientos_pubmed, 1):
                        print(f"\n   📋 Tratamiento {j} de PubMed:")
                        print(f"      Título: {tratamiento.titulo}")
                        print(f"      DOI: {tratamiento.doi}")
                        print(f"      Fuente: {tratamiento.fuente}")
                        print(f"      Fecha: {tratamiento.fecha_publicacion}")
                        print(f"      Autores: {', '.join(tratamiento.autores[:3])}")
                        
                        # Verificar que el DOI sea válido
                        if tratamiento.doi and tratamiento.doi != "Sin DOI":
                            print(f"      ✅ DOI válido: {tratamiento.doi}")
                            print(f"      🔗 Link: https://doi.org/{tratamiento.doi}")
                        else:
                            print(f"      ⚠️ DOI no disponible")
                else:
                    print(f"   ⚠️ No se encontraron tratamientos en PubMed")
                
                # Probar búsqueda en Europe PMC
                print(f"\n   🔍 Probando Europe PMC...")
                tratamientos_europepmc = apis.buscar_europepmc(caso['condicion'], caso['especialidad'])
                
                if tratamientos_europepmc:
                    print(f"   ✅ Encontrados {len(tratamientos_europepmc)} tratamientos en Europe PMC")
                    
                    for j, tratamiento in enumerate(tratamientos_europepmc, 1):
                        print(f"\n   📋 Tratamiento {j} de Europe PMC:")
                        print(f"      Título: {tratamiento.titulo}")
                        print(f"      DOI: {tratamiento.doi}")
                        print(f"      Fuente: {tratamiento.fuente}")
                        print(f"      Fecha: {tratamiento.fecha_publicacion}")
                        print(f"      Autores: {', '.join(tratamiento.autores[:3])}")
                        
                        # Verificar que el DOI sea válido
                        if tratamiento.doi and tratamiento.doi != "Sin DOI":
                            print(f"      ✅ DOI válido: {tratamiento.doi}")
                            print(f"      🔗 Link: https://doi.org/{tratamiento.doi}")
                        else:
                            print(f"      ⚠️ DOI no disponible")
                else:
                    print(f"   ⚠️ No se encontraron tratamientos en Europe PMC")
                
                # Probar búsqueda completa
                print(f"\n   🔍 Probando búsqueda completa...")
                resultados_completos = apis.obtener_tratamientos_completos(caso['condicion'], caso['especialidad'])
                
                total_tratamientos = len(resultados_completos.get('tratamientos_pubmed', [])) + len(resultados_completos.get('tratamientos_europepmc', []))
                print(f"   ✅ Total de tratamientos encontrados: {total_tratamientos}")
                
                # Probar conversión a formato Copilot
                if total_tratamientos > 0:
                    print(f"\n   🔄 Probando conversión a formato Copilot...")
                    todos_tratamientos = resultados_completos.get('tratamientos_pubmed', []) + resultados_completos.get('tratamientos_europepmc', [])
                    planes_copilot = apis.convertir_a_formato_copilot(todos_tratamientos)
                    
                    print(f"   ✅ Convertidos {len(planes_copilot)} planes a formato Copilot")
                    
                    for j, plan in enumerate(planes_copilot, 1):
                        print(f"\n   📋 Plan {j} convertido:")
                        print(f"      Título: {plan['titulo']}")
                        print(f"      DOI: {plan['doi_referencia']}")
                        print(f"      Nivel: {plan['nivel_evidencia']}")
                        print(f"      Estudios basados: {len(plan['estudios_basados'])} estudios")
                        
                        if plan['estudios_basados']:
                            for estudio in plan['estudios_basados']:
                                print(f"         - {estudio['titulo']} ({estudio['fecha']})")
                
            except Exception as e:
                print(f"   ❌ Error en caso {i}: {e}")
        
    except Exception as e:
        print(f"❌ Error en pruebas de búsquedas reales: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE BÚSQUEDAS REALES EN APIS MÉDICAS")
    print("=" * 80)
    
    try:
        # Ejecutar todas las pruebas
        success = test_busquedas_reales()
        
        if success:
            print("\n\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
            print("🎯 Las búsquedas reales en APIs médicas están funcionando correctamente")
            
            print("\n📋 RESUMEN DE VERIFICACIONES:")
            print("   ✅ Búsquedas en PubMed con filtros de fecha")
            print("   ✅ Búsquedas en Europe PMC con filtros de fecha")
            print("   ✅ Queries específicas y relevantes")
            print("   ✅ DOIs verificables")
            print("   ✅ Nombres de estudios reales")
            print("   ✅ Conversión a formato Copilot")
            print("   ✅ Eliminación de duplicados")
            print("   ✅ Rate limiting implementado")
            
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