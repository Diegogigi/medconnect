#!/usr/bin/env python3
"""
Script para probar Europe PMC directamente
"""

import requests
import json

def test_europepmc_directo():
    """Prueba Europe PMC directamente"""
    print("🔍 PRUEBA DIRECTA DE EUROPE PMC")
    print("=" * 40)
    
    # Probar búsqueda simple con parámetros correctos
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        'query': 'back pain',
        'format': 'json',
        'pageSize': 5
    }
    
    try:
        print("🔍 Probando búsqueda: 'back pain'")
        response = requests.get(url, params=params, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 URL completa: {response.url}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ JSON válido recibido")
                print(f"📊 Estructura: {list(data.keys())}")
                
                if 'resultList' in data:
                    result_list = data['resultList']
                    print(f"📊 ResultList keys: {list(result_list.keys())}")
                    
                    if 'result' in result_list:
                        resultados = result_list['result']
                        print(f"✅ Encontrados {len(resultados)} artículos")
                        
                        if resultados:
                            primer_resultado = resultados[0]
                            print(f"📄 Primer artículo:")
                            print(f"   Título: {primer_resultado.get('title', 'Sin título')}")
                            print(f"   DOI: {primer_resultado.get('doi', 'Sin DOI')}")
                            print(f"   Fuente: {primer_resultado.get('source', 'Sin fuente')}")
                            print(f"   Año: {primer_resultado.get('pubYear', 'Sin año')}")
                    else:
                        print("❌ No hay 'result' en resultList")
                        print(f"ResultList completo: {result_list}")
                else:
                    print("❌ No hay 'resultList' en la respuesta")
                    print(f"Respuesta completa: {data}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"Respuesta: {response.text[:500]}...")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Respuesta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_europepmc_terminos_especificos():
    """Prueba términos específicos en Europe PMC"""
    print("\n🔍 PRUEBA CON TÉRMINOS ESPECÍFICOS")
    print("=" * 40)
    
    terminos_prueba = [
        'physical therapy',
        'rehabilitation',
        'exercise',
        'treatment',
        'therapy'
    ]
    
    for termino in terminos_prueba:
        print(f"\n🔍 Probando: '{termino}'")
        
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        params = {
            'query': termino,
            'format': 'json',
            'pageSize': 3
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if 'resultList' in data and 'result' in data['resultList']:
                        resultados = data['resultList']['result']
                        print(f"✅ Encontrados {len(resultados)} artículos")
                        
                        if resultados:
                            primer_resultado = resultados[0]
                            titulo = primer_resultado.get('title', 'Sin título')
                            print(f"📄 Primer resultado: {titulo[:100]}...")
                    else:
                        print("❌ Respuesta inesperada")
                        print(f"Estructura: {list(data.keys())}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Error JSON: {e}")
            else:
                print(f"❌ Error HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        import time
        time.sleep(1)  # Pausa entre búsquedas

def test_europepmc_conectividad():
    """Prueba la conectividad básica"""
    print("\n🔍 PRUEBA DE CONECTIVIDAD")
    print("=" * 30)
    
    try:
        # Probar conectividad básica
        response = requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search", timeout=5)
        print(f"✅ Conectividad básica: {response.status_code}")
        
        # Probar con parámetros mínimos
        params = {'query': 'test', 'format': 'json'}
        response = requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search", params=params, timeout=5)
        print(f"✅ Búsqueda mínima: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error de conectividad: {e}")

def main():
    """Función principal"""
    print("🔍 PRUEBAS DE EUROPE PMC")
    print("=" * 50)
    
    # Probar conectividad
    test_europepmc_conectividad()
    
    # Probar búsqueda directa
    test_europepmc_directo()
    
    # Probar términos específicos
    test_europepmc_terminos_especificos()
    
    print("\n✅ Todas las pruebas completadas")

if __name__ == "__main__":
    main() 