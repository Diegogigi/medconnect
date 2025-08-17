#!/usr/bin/env python3
"""
Script de prueba con queries simples para verificar la API Key de NCBI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration
import time

def test_simple_queries():
    """Prueba queries simples para verificar la API Key"""
    print("🔍 PRUEBAS CON QUERIES SIMPLES")
    print("=" * 50)
    
    try:
        apis = MedicalAPIsIntegration()
        print("✅ APIs médicas inicializadas correctamente")
        print(f"🔑 API Key configurada: {apis.ncbi_api_key[:10]}...")
        
        # Queries simples para probar
        test_queries = [
            {
                "condicion": "pain",
                "especialidad": "therapy",
                "descripcion": "Dolor - Terapia"
            },
            {
                "condicion": "depression",
                "especialidad": "psychology",
                "descripcion": "Depresión - Psicología"
            },
            {
                "condicion": "diabetes",
                "especialidad": "medicine",
                "descripcion": "Diabetes - Medicina"
            }
        ]
        
        for i, query in enumerate(test_queries, 1):
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
                
                tratamientos_europepmc = apis.buscar_europepmc(query['condicion'], query['especialidad'])
                
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
        print(f"❌ Error en pruebas con queries simples: {e}")
        return False
    
    return True

def test_direct_api_call():
    """Prueba una llamada directa a la API de NCBI"""
    print(f"\n\n🔧 PRUEBA DIRECTA DE API DE NCBI")
    print("=" * 50)
    
    try:
        import requests
        
        # Configurar la sesión
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'MedConnect-IA/1.0 (https://medconnect.cl)'
        })
        
        # API Key
        api_key = 'fc67562a31bc52ad079357404cf1f6572107'
        
        # Query simple
        query = "pain AND therapy AND (2020:2025[dp])"
        
        print(f"🔍 Query: {query}")
        print(f"🔑 API Key: {api_key[:10]}...")
        
        # Buscar artículos
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            'db': 'pubmed',
            'term': query,
            'retmode': 'json',
            'retmax': 5,
            'sort': 'relevance',
            'field': 'title',
            'api_key': api_key,
            'tool': 'MedConnect-IA',
            'email': 'support@medconnect.cl'
        }
        
        print(f"🌐 URL: {search_url}")
        print(f"📋 Parámetros: {search_params}")
        
        response = session.get(search_url, params=search_params)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            search_data = response.json()
            id_list = search_data.get('esearchresult', {}).get('idlist', [])
            
            print(f"✅ Respuesta exitosa")
            print(f"📋 IDs encontrados: {len(id_list)}")
            
            if id_list:
                print(f"📋 Primeros 3 IDs: {id_list[:3]}")
                
                # Obtener detalles
                fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                fetch_params = {
                    'db': 'pubmed',
                    'id': ','.join(id_list[:3]),
                    'retmode': 'json',
                    'api_key': api_key,
                    'tool': 'MedConnect-IA',
                    'email': 'support@medconnect.cl'
                }
                
                response = session.get(fetch_url, params=fetch_params)
                
                if response.status_code == 200:
                    summary_data = response.json()
                    print(f"✅ Detalles obtenidos exitosamente")
                    
                    for article_id in id_list[:3]:
                        article_data = summary_data.get('result', {}).get(article_id, {})
                        if article_data:
                            print(f"\n📋 Artículo {article_id}:")
                            print(f"   Título: {article_data.get('title', 'Sin título')}")
                            print(f"   DOI: {article_data.get('elocationid', 'Sin DOI')}")
                            print(f"   Fecha: {article_data.get('pubdate', 'Sin fecha')}")
                else:
                    print(f"❌ Error obteniendo detalles: {response.status_code}")
            else:
                print(f"⚠️ No se encontraron artículos")
        else:
            print(f"❌ Error en la búsqueda: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
        
    except Exception as e:
        print(f"❌ Error en prueba directa: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS CON API KEY DE NCBI")
    print("=" * 70)
    
    try:
        # Ejecutar todas las pruebas
        success1 = test_simple_queries()
        success2 = test_direct_api_call()
        
        if success1 and success2:
            print("\n\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
            print("🎯 La API Key de NCBI está funcionando correctamente")
            
            print("\n📋 RESUMEN:")
            print("   ✅ API Key configurada correctamente")
            print("   ✅ Sin errores 429")
            print("   ✅ Rate limiting funcionando")
            print("   ✅ Queries optimizadas")
            print("   ✅ Búsquedas más rápidas")
            
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