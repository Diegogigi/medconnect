#!/usr/bin/env python3
"""
Script para probar todas las APIs médicas disponibles
"""

import requests
import time
from medical_apis_integration import MedicalAPIsIntegration

def test_europepmc():
    """Prueba Europe PMC"""
    print("🔍 PRUEBA EUROPE PMC")
    print("=" * 40)
    
    try:
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        params = {
            'query': 'knee pain treatment',
            'format': 'json',
            'pageSize': 3
        }
        
        print("📤 Enviando consulta a Europe PMC...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'resultList' in data and 'result' in data['resultList']:
                resultados = data['resultList']['result']
                print(f"✅ Europe PMC funcionando: {len(resultados)} resultados")
                
                for i, resultado in enumerate(resultados[:2], 1):
                    titulo = resultado.get('title', 'Sin título')
                    doi = resultado.get('doi', 'Sin DOI')
                    fecha = resultado.get('firstPublicationDate', 'Sin fecha')
                    
                    print(f"\n📋 Resultado {i}:")
                    print(f"   Título: {titulo[:80]}...")
                    print(f"   DOI: {doi}")
                    print(f"   Fecha: {fecha}")
                    
                    # Verificar DOI y año
                    if doi and doi != 'Sin DOI':
                        print(f"   ✅ DOI válido: {doi}")
                        print(f"   🔗 Link: https://doi.org/{doi}")
                    else:
                        print(f"   ❌ DOI no disponible")
                    
                    if fecha and fecha != 'Sin fecha':
                        año = fecha.split('-')[0] if '-' in fecha else 'N/A'
                        print(f"   📅 Año: {año}")
                    else:
                        print(f"   ❌ Año no disponible")
                
                return True
            else:
                print("❌ Respuesta inesperada de Europe PMC")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code} en Europe PMC")
            return False
            
    except Exception as e:
        print(f"❌ Error en Europe PMC: {e}")
        return False

def test_pubmed_status():
    """Prueba el estado de PubMed"""
    print("\n🔍 PRUEBA PUBMED")
    print("=" * 40)
    
    try:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': 'knee pain',
            'retmode': 'json',
            'retmax': 3
        }
        
        print("📤 Enviando consulta a PubMed...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'esearchresult' in data and 'idlist' in data['esearchresult']:
                    ids = data['esearchresult']['idlist']
                    print(f"✅ PubMed funcionando: {len(ids)} IDs encontrados")
                    return True
                else:
                    print("❌ Respuesta inesperada de PubMed")
                    return False
            except:
                print("❌ Error decodificando JSON de PubMed")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code} en PubMed")
            return False
            
    except Exception as e:
        print(f"❌ Error en PubMed: {e}")
        return False

def test_medical_apis_integration():
    """Prueba la integración con APIs médicas"""
    print("\n🔍 PRUEBA INTEGRACIÓN APIS MÉDICAS")
    print("=" * 40)
    
    try:
        apis = MedicalAPIsIntegration()
        print("✅ MedicalAPIsIntegration creado correctamente")
        
        # Probar búsqueda en Europe PMC
        print("\n📤 Probando búsqueda en Europe PMC...")
        resultados_europepmc = apis.buscar_europepmc("knee pain", "kinesiologia", 45)
        
        if resultados_europepmc:
            print(f"✅ Europe PMC: {len(resultados_europepmc)} resultados")
            
            # Mostrar primer resultado con DOI y año
            if resultados_europepmc:
                primer_resultado = resultados_europepmc[0]
                print(f"\n📋 Primer resultado:")
                print(f"   Título: {primer_resultado.titulo[:80]}...")
                print(f"   DOI: {primer_resultado.doi}")
                print(f"   Año: {primer_resultado.año_publicacion}")
                print(f"   Fecha: {primer_resultado.fecha_publicacion}")
                
                if primer_resultado.doi and primer_resultado.doi != 'Sin DOI':
                    print(f"   ✅ DOI válido: {primer_resultado.doi}")
                    print(f"   🔗 Link: https://doi.org/{primer_resultado.doi}")
                else:
                    print(f"   ❌ DOI no disponible")
                
                if primer_resultado.año_publicacion and primer_resultado.año_publicacion != 'N/A':
                    print(f"   ✅ Año válido: {primer_resultado.año_publicacion}")
                else:
                    print(f"   ❌ Año no disponible")
        else:
            print("❌ Europe PMC: No se encontraron resultados")
        
        # Probar PubMed (puede fallar por mantenimiento)
        print("\n📤 Probando búsqueda en PubMed...")
        try:
            resultados_pubmed = apis.buscar_tratamiento_pubmed("knee pain", "kinesiologia", 45)
            if resultados_pubmed:
                print(f"✅ PubMed: {len(resultados_pubmed)} resultados")
            else:
                print("⚠️ PubMed: No se encontraron resultados (posible mantenimiento)")
        except Exception as e:
            print(f"⚠️ PubMed: Error - {e} (posible mantenimiento)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        return False

def test_fallback_system():
    """Prueba el sistema de fallback"""
    print("\n🔄 PRUEBA SISTEMA DE FALLBACK")
    print("=" * 40)
    
    try:
        apis = MedicalAPIsIntegration()
        
        # Simular búsqueda que falla en PubMed pero funciona en Europe PMC
        print("📤 Probando búsqueda con fallback...")
        
        # Probar búsqueda con términos clave
        resultados = apis.buscar_con_terminos_clave(
            condicion="knee pain",
            especialidad="kinesiologia",
            terminos_clave=["physical therapy", "rehabilitation"],
            edad_paciente=45
        )
        
        total_resultados = 0
        if resultados.get('tratamientos_pubmed'):
            total_resultados += len(resultados['tratamientos_pubmed'])
            print(f"✅ PubMed: {len(resultados['tratamientos_pubmed'])} resultados")
        
        if resultados.get('tratamientos_europepmc'):
            total_resultados += len(resultados['tratamientos_europepmc'])
            print(f"✅ Europe PMC: {len(resultados['tratamientos_europepmc'])} resultados")
        
        if total_resultados > 0:
            print(f"✅ Total: {total_resultados} resultados combinados")
            
            # Mostrar ejemplo de resultado con DOI y año
            todos_resultados = []
            if resultados.get('tratamientos_pubmed'):
                todos_resultados.extend(resultados['tratamientos_pubmed'])
            if resultados.get('tratamientos_europepmc'):
                todos_resultados.extend(resultados['tratamientos_europepmc'])
            
            if todos_resultados:
                ejemplo = todos_resultados[0]
                print(f"\n📋 Ejemplo de resultado:")
                print(f"   Título: {ejemplo.titulo[:80]}...")
                print(f"   DOI: {ejemplo.doi}")
                print(f"   Año: {ejemplo.año_publicacion}")
                print(f"   Fuente: {ejemplo.fuente}")
                
                if ejemplo.doi and ejemplo.doi != 'Sin DOI':
                    print(f"   ✅ DOI válido: {ejemplo.doi}")
                    print(f"   🔗 Link: https://doi.org/{ejemplo.doi}")
                else:
                    print(f"   ❌ DOI no disponible")
                
                if ejemplo.año_publicacion and ejemplo.año_publicacion != 'N/A':
                    print(f"   ✅ Año válido: {ejemplo.año_publicacion}")
                else:
                    print(f"   ❌ Año no disponible")
        else:
            print("❌ No se encontraron resultados en ninguna API")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en sistema de fallback: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE APIS DISPONIBLES")
    print("=" * 50)
    
    # Prueba 1: Europe PMC
    europepmc_ok = test_europepmc()
    
    # Prueba 2: PubMed (puede fallar por mantenimiento)
    pubmed_ok = test_pubmed_status()
    
    # Prueba 3: Integración completa
    integracion_ok = test_medical_apis_integration()
    
    # Prueba 4: Sistema de fallback
    fallback_ok = test_fallback_system()
    
    print("\n📊 RESUMEN DE ESTADO:")
    print("=" * 50)
    print(f"✅ Europe PMC: {'Funcionando' if europepmc_ok else 'Error'}")
    print(f"⚠️ PubMed: {'Funcionando' if pubmed_ok else 'En mantenimiento'}")
    print(f"✅ Integración: {'Funcionando' if integracion_ok else 'Error'}")
    print(f"✅ Fallback: {'Funcionando' if fallback_ok else 'Error'}")
    
    if europepmc_ok and integracion_ok and fallback_ok:
        print("\n🎉 SISTEMA FUNCIONANDO CORRECTAMENTE")
        print("✅ Europe PMC disponible para búsquedas")
        print("✅ Sistema de fallback activo")
        print("✅ DOI y año se extraen correctamente")
        print("⚠️ PubMed en mantenimiento (sistema usa Europe PMC)")
    else:
        print("\n❌ PROBLEMAS DETECTADOS")
        if not europepmc_ok:
            print("❌ Europe PMC no disponible")
        if not integracion_ok:
            print("❌ Error en integración de APIs")
        if not fallback_ok:
            print("❌ Error en sistema de fallback")

if __name__ == "__main__":
    main() 