#!/usr/bin/env python3
"""
Script simple para probar una query básica
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration
import time

def test_query_simple():
    """Prueba una query muy simple"""
    print("🔍 PRUEBA DE QUERY SIMPLE")
    print("=" * 40)
    
    try:
        apis = MedicalAPIsIntegration()
        print("✅ APIs médicas inicializadas correctamente")
        
        # Query muy simple
        condicion = "pain"
        especialidad = "therapy"
        
        print(f"🔍 Query: '{condicion}' en '{especialidad}'")
        
        # Probar PubMed
        print(f"\n   🔍 Probando PubMed...")
        start_time = time.time()
        
        tratamientos_pubmed = apis.buscar_tratamiento_pubmed(condicion, especialidad)
        
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
        
        # Probar Europe PMC
        print(f"\n   🔍 Probando Europe PMC...")
        start_time = time.time()
        
        tratamientos_europepmc = apis.buscar_europepmc(condicion, especialidad)
        
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
        print(f"❌ Error en prueba de query simple: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBA DE QUERY SIMPLE")
    print("=" * 50)
    
    try:
        success = test_query_simple()
        
        if success:
            print("\n\n✅ PRUEBA COMPLETADA EXITOSAMENTE")
            print("🎯 La query simple está funcionando")
            
        else:
            print("\n❌ LA PRUEBA FALLÓ")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR EN LA PRUEBA: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 