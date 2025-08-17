#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de búsqueda de tratamientos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration

def test_busqueda_tratamiento():
    """Prueba la búsqueda de tratamientos"""
    print("🔍 PRUEBAS DE BÚSQUEDA DE TRATAMIENTOS")
    print("=" * 50)
    
    # Inicializar la integración de APIs
    apis = MedicalAPIsIntegration()
    
    # Casos de prueba
    casos_prueba = [
        {
            'condicion': 'Dolor lumbar de 3 semanas',
            'especialidad': 'kinesiologia',
            'descripcion': 'Dolor lumbar - Kinesiología'
        },
        {
            'condicion': 'Dificultad para tragar alimentos',
            'especialidad': 'fonoaudiologia',
            'descripcion': 'Problemas de deglución - Fonoaudiología'
        },
        {
            'condicion': 'Ansiedad y estrés laboral',
            'especialidad': 'psicologia',
            'descripcion': 'Ansiedad - Psicología'
        },
        {
            'condicion': 'Pérdida de peso y fatiga',
            'especialidad': 'nutricion',
            'descripcion': 'Pérdida de peso - Nutrición'
        }
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n📋 Caso {i}: {caso['descripcion']}")
        print(f"Condición: {caso['condicion']}")
        print(f"Especialidad: {caso['especialidad']}")
        
        try:
            # Probar búsqueda en PubMed
            print(f"\n🔍 Probando búsqueda PubMed...")
            tratamientos_pubmed = apis.buscar_tratamiento_pubmed(
                caso['condicion'], 
                caso['especialidad']
            )
            
            if tratamientos_pubmed:
                print(f"✅ Encontrados {len(tratamientos_pubmed)} tratamientos en PubMed")
                for j, tratamiento in enumerate(tratamientos_pubmed[:3], 1):
                    print(f"   {j}. {tratamiento.titulo}")
                    print(f"      DOI: {tratamiento.doi}")
                    print(f"      Fuente: {tratamiento.fuente}")
            else:
                print(f"⚠️ No se encontraron tratamientos en PubMed")
            
            # Probar búsqueda en Europe PMC
            print(f"\n🔍 Probando búsqueda Europe PMC...")
            tratamientos_europepmc = apis.buscar_europepmc(
                caso['condicion'], 
                caso['especialidad']
            )
            
            if tratamientos_europepmc:
                print(f"✅ Encontrados {len(tratamientos_europepmc)} tratamientos en Europe PMC")
                for j, tratamiento in enumerate(tratamientos_europepmc[:3], 1):
                    print(f"   {j}. {tratamiento.titulo}")
                    print(f"      DOI: {tratamiento.doi}")
                    print(f"      Fuente: {tratamiento.fuente}")
            else:
                print(f"⚠️ No se encontraron tratamientos en Europe PMC")
            
            # Probar búsqueda completa
            print(f"\n🔍 Probando búsqueda completa...")
            resultados_completos = apis.obtener_tratamientos_completos(
                caso['condicion'], 
                caso['especialidad']
            )
            
            total_tratamientos = len(resultados_completos.get('tratamientos_pubmed', [])) + len(resultados_completos.get('tratamientos_europepmc', []))
            print(f"✅ Total de tratamientos encontrados: {total_tratamientos}")
            
            if total_tratamientos > 0:
                print("✅ Búsqueda funcionando correctamente")
            else:
                print("⚠️ No se encontraron resultados")
                
        except Exception as e:
            print(f"❌ Error en caso {i}: {e}")
            continue
        
        print("-" * 60)

def test_api_keys():
    """Prueba las API keys"""
    print("\n🔑 PRUEBAS DE API KEYS")
    print("=" * 30)
    
    apis = MedicalAPIsIntegration()
    
    # Verificar API key de NCBI
    if apis.ncbi_api_key:
        print(f"✅ API key de NCBI configurada: {apis.ncbi_api_key[:10]}...")
    else:
        print("❌ API key de NCBI no configurada")
    
    # Verificar API key de FDA (si existe)
    if hasattr(apis, 'fda_api_key') and apis.fda_api_key:
        print(f"✅ API key de FDA configurada: {apis.fda_api_key[:10]}...")
    else:
        print("⚠️ API key de FDA no configurada (opcional)")

def test_conexion_apis():
    """Prueba la conexión a las APIs"""
    print("\n🌐 PRUEBAS DE CONEXIÓN")
    print("=" * 30)
    
    import requests
    
    # Probar conexión a PubMed
    try:
        response = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", 
                              params={'db': 'pubmed', 'term': 'test', 'retmode': 'json'}, 
                              timeout=10)
        if response.status_code == 200:
            print("✅ Conexión a PubMed funcionando")
        else:
            print(f"❌ Error de conexión a PubMed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión a PubMed: {e}")
    
    # Probar conexión a Europe PMC
    try:
        response = requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search", 
                              params={'query': 'test', 'format': 'json'}, 
                              timeout=10)
        if response.status_code == 200:
            print("✅ Conexión a Europe PMC funcionando")
        else:
            print(f"❌ Error de conexión a Europe PMC: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión a Europe PMC: {e}")

def main():
    """Función principal"""
    print("🔍 PRUEBAS DE BÚSQUEDA DE TRATAMIENTOS")
    print("=" * 50)
    
    # Probar API keys
    test_api_keys()
    
    # Probar conexiones
    test_conexion_apis()
    
    # Probar búsquedas
    test_busqueda_tratamiento()
    
    print("\n✅ Todas las pruebas completadas")
    print("\n📋 Resumen:")
    print("   • Verificación de API keys")
    print("   • Pruebas de conexión a APIs")
    print("   • Búsquedas en PubMed y Europe PMC")
    print("   • Casos de prueba con diferentes especialidades")

if __name__ == "__main__":
    main() 