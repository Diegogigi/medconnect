#!/usr/bin/env python3
"""
Script de prueba para verificar la búsqueda real en PubMed
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration
import requests
import json

def test_conexion_pubmed_directa():
    """Prueba la conexión directa a PubMed"""
    print("🔍 PRUEBA DE CONEXIÓN DIRECTA A PUBMED")
    print("=" * 50)
    
    # Probar búsqueda simple
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        'db': 'pubmed',
        'term': 'back pain',
        'retmode': 'json',
        'retmax': 3,
        'sort': 'relevance'
    }
    
    try:
        print("🔍 Probando búsqueda simple: 'back pain'")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'esearchresult' in data and 'idlist' in data['esearchresult']:
                    ids = data['esearchresult']['idlist']
                    print(f"✅ Encontrados {len(ids)} artículos")
                    print(f"📋 IDs: {ids}")
                    
                    # Probar obtener detalles
                    if ids:
                        test_obtener_detalles(ids[:2])
                else:
                    print("❌ Respuesta inesperada de PubMed")
                    print(f"Respuesta: {data}")
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"Respuesta: {response.text[:200]}...")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Respuesta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_obtener_detalles(ids):
    """Prueba obtener detalles de artículos"""
    print(f"\n🔍 Probando obtener detalles para IDs: {ids}")
    
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        'db': 'pubmed',
        'id': ','.join(ids),
        'retmode': 'json'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'result' in data:
                    for pmid, info in data['result'].items():
                        if pmid == 'uids':
                            continue
                        
                        titulo = info.get('title', 'Sin título')
                        autores = info.get('authors', [])
                        fecha = info.get('pubdate', 'Fecha no disponible')
                        
                        print(f"📄 Artículo {pmid}:")
                        print(f"   Título: {titulo}")
                        print(f"   Autores: {autores}")
                        print(f"   Fecha: {fecha}")
                        print()
                        
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error obteniendo detalles: {e}")

def test_busqueda_con_api_key():
    """Prueba búsqueda con API key"""
    print("\n🔑 PRUEBA CON API KEY")
    print("=" * 30)
    
    apis = MedicalAPIsIntegration()
    
    if not apis.ncbi_api_key:
        print("❌ No hay API key configurada")
        return
    
    print(f"✅ API key configurada: {apis.ncbi_api_key[:10]}...")
    
    # Probar búsqueda simple
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        'db': 'pubmed',
        'term': 'physical therapy',
        'retmode': 'json',
        'retmax': 3,
        'sort': 'relevance',
        'api_key': apis.ncbi_api_key,
        'tool': 'MedConnect-IA',
        'email': 'support@medconnect.cl'
    }
    
    try:
        print("🔍 Probando búsqueda con API key: 'physical therapy'")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'esearchresult' in data and 'idlist' in data['esearchresult']:
                    ids = data['esearchresult']['idlist']
                    print(f"✅ Encontrados {len(ids)} artículos con API key")
                    print(f"📋 IDs: {ids}")
                else:
                    print("❌ Respuesta inesperada")
                    print(f"Respuesta: {data}")
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"Respuesta: {response.text[:200]}...")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Respuesta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_busqueda_completa():
    """Prueba la búsqueda completa del sistema"""
    print("\n🔍 PRUEBA DE BÚSQUEDA COMPLETA")
    print("=" * 40)
    
    apis = MedicalAPIsIntegration()
    
    # Caso de prueba
    condicion = "Dolor lumbar de 3 semanas"
    especialidad = "kinesiologia"
    
    print(f"🔍 Búsqueda: '{condicion}' en '{especialidad}'")
    
    try:
        resultados = apis.obtener_tratamientos_completos(condicion, especialidad)
        
        total_pubmed = len(resultados.get('tratamientos_pubmed', []))
        total_europepmc = len(resultados.get('tratamientos_europepmc', []))
        
        print(f"✅ Resultados PubMed: {total_pubmed}")
        print(f"✅ Resultados Europe PMC: {total_europepmc}")
        print(f"✅ Total: {total_pubmed + total_europepmc}")
        
        if total_pubmed + total_europepmc > 0:
            print("✅ Búsqueda funcionando correctamente")
            
            # Mostrar algunos resultados
            if resultados.get('tratamientos_pubmed'):
                print("\n📄 Primer resultado PubMed:")
                primer_resultado = resultados['tratamientos_pubmed'][0]
                print(f"   Título: {primer_resultado.titulo}")
                print(f"   DOI: {primer_resultado.doi}")
                print(f"   Fuente: {primer_resultado.fuente}")
        else:
            print("⚠️ No se encontraron resultados")
            
    except Exception as e:
        print(f"❌ Error en búsqueda completa: {e}")

def main():
    """Función principal"""
    print("🔍 PRUEBAS DE BÚSQUEDA REAL EN PUBMED")
    print("=" * 50)
    
    # Probar conexión directa
    test_conexion_pubmed_directa()
    
    # Probar con API key
    test_busqueda_con_api_key()
    
    # Probar búsqueda completa
    test_busqueda_completa()
    
    print("\n✅ Todas las pruebas completadas")

if __name__ == "__main__":
    main() 