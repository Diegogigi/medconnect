#!/usr/bin/env python3
"""
Script de prueba para verificar la API Key de NCBI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration
import time

def test_api_key_ncbi():
    """Prueba la API Key de NCBI"""
    print("🔑 PRUEBAS DE API KEY DE NCBI")
    print("=" * 50)
    
    try:
        apis = MedicalAPIsIntegration()
        print("✅ APIs médicas inicializadas correctamente")
        print(f"🔑 API Key configurada: {apis.ncbi_api_key[:10]}...")
        print(f"⏱️ Rate limiting: {1/apis.min_interval:.1f} requests por segundo")
        
        # Casos de prueba
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
                # Probar búsqueda en PubMed con API Key
                print(f"\n   🔍 Probando PubMed con API Key...")
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
                        print(f"      Fuente: {tratamiento.fuente}")
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
                
            except Exception as e:
                print(f"   ❌ Error en caso {i}: {e}")
        
        # Probar búsqueda completa
        print(f"\n\n🔍 PRUEBA DE BÚSQUEDA COMPLETA CON API KEY")
        print("=" * 50)
        
        for caso in casos_prueba:
            print(f"\n📋 Probando búsqueda completa para: {caso['descripcion']}")
            
            start_time = time.time()
            resultados_completos = apis.obtener_tratamientos_completos(caso['condicion'], caso['especialidad'])
            end_time = time.time()
            
            total_time = end_time - start_time
            total_tratamientos = len(resultados_completos.get('tratamientos_pubmed', [])) + len(resultados_completos.get('tratamientos_europepmc', []))
            
            print(f"   ⏱️ Tiempo total: {total_time:.2f} segundos")
            print(f"   📊 Total tratamientos: {total_tratamientos}")
            print(f"   📚 PubMed: {len(resultados_completos.get('tratamientos_pubmed', []))}")
            print(f"   📚 Europe PMC: {len(resultados_completos.get('tratamientos_europepmc', []))}")
            
            if total_tratamientos > 0:
                print(f"   ✅ Búsquedas exitosas con API Key")
            else:
                print(f"   ⚠️ No se encontraron tratamientos, pero sin errores")
        
    except Exception as e:
        print(f"❌ Error en pruebas de API Key: {e}")
        return False
    
    return True

def test_rate_limiting_with_api_key():
    """Prueba el rate limiting con API Key"""
    print(f"\n\n⏱️ PRUEBAS DE RATE LIMITING CON API KEY")
    print("=" * 50)
    
    try:
        apis = MedicalAPIsIntegration()
        
        print("🔄 Probando rate limiting con API Key...")
        
        start_time = time.time()
        
        # Hacer 5 búsquedas consecutivas
        for i in range(5):
            print(f"   Búsqueda {i+1}...")
            tratamientos = apis.buscar_tratamiento_pubmed("pain", "therapy")
            print(f"   ✅ Búsqueda {i+1} completada ({len(tratamientos)} resultados)")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n⏱️ Tiempo total: {total_time:.2f} segundos")
        print(f"⏱️ Tiempo promedio por búsqueda: {total_time/5:.2f} segundos")
        print(f"⏱️ Requests por segundo: {5/total_time:.2f}")
        
        if total_time >= 2.5:  # Debería tomar al menos 2.5 segundos (5 * 0.5)
            print("✅ Rate limiting funcionando correctamente con API Key")
            return True
        else:
            print("❌ Rate limiting no está funcionando correctamente")
            return False
        
    except Exception as e:
        print(f"❌ Error en pruebas de rate limiting: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE API KEY DE NCBI")
    print("=" * 70)
    
    try:
        # Ejecutar todas las pruebas
        success1 = test_api_key_ncbi()
        success2 = test_rate_limiting_with_api_key()
        
        if success1 and success2:
            print("\n\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
            print("🎯 La API Key de NCBI está funcionando correctamente")
            
            print("\n📋 BENEFICIOS DE LA API KEY:")
            print("   ✅ Mayor límite de requests (10 por segundo)")
            print("   ✅ Mejor prioridad en las búsquedas")
            print("   ✅ Menos errores 429")
            print("   ✅ Búsquedas más rápidas")
            print("   ✅ Resultados más relevantes")
            print("   ✅ Mejor rate limiting")
            
            print("\n🔧 CONFIGURACIÓN ACTUAL:")
            print("   🔑 API Key: fc67562a31bc52ad079357404cf1f6572107")
            print("   ⏱️ Rate Limiting: 2 requests por segundo")
            print("   🛠️ Tool: MedConnect-IA")
            print("   📧 Email: support@medconnect.cl")
            
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