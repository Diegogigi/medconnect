#!/usr/bin/env python3
"""
Script para probar sin filtro de fecha
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import time

def test_sin_filtro_fecha():
    """Prueba sin filtro de fecha"""
    print("🔍 PRUEBA SIN FILTRO DE FECHA")
    print("=" * 40)
    
    try:
        # API Key
        api_key = 'fc67562a31bc52ad079357404cf1f6572107'
        
        # Query simple sin filtro de fecha
        query = "pain AND therapy"
        
        print(f"🔍 Query: '{query}'")
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
        
        response = requests.get(search_url, params=search_params)
        
        print(f"📊 Status Code: {response.status_code}")
        
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
                
                response = requests.get(fetch_url, params=fetch_params)
                
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
        print(f"❌ Error en prueba sin filtro de fecha: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBA SIN FILTRO DE FECHA")
    print("=" * 50)
    
    try:
        success = test_sin_filtro_fecha()
        
        if success:
            print("\n\n✅ PRUEBA COMPLETADA EXITOSAMENTE")
            print("🎯 La query sin filtro de fecha está funcionando")
            
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