#!/usr/bin/env python3
"""
Script para probar el filtrado de papers más relevantes
"""

import sys
import os
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration

def test_filtrado_papers():
    """Prueba el filtrado de papers más relevantes"""
    print("🎯 PRUEBA DE FILTRADO DE PAPERS MÁS RELEVANTES")
    print("=" * 60)
    
    try:
        # Inicializar APIs
        apis = MedicalAPIsIntegration()
        
        # Casos de prueba específicos
        casos_prueba = [
            {
                'condicion': 'dolor de rodilla',
                'especialidad': 'kinesiologia',
                'edad': 45,
                'descripcion': 'Dolor de rodilla en adulto'
            },
            {
                'condicion': 'problemas de habla',
                'especialidad': 'fonoaudiologia',
                'edad': 8,
                'descripcion': 'Problemas de habla en niño'
            },
            {
                'condicion': 'lesión de hombro',
                'especialidad': 'fisioterapia',
                'edad': 35,
                'descripcion': 'Lesión de hombro en adulto joven'
            }
        ]
        
        for i, caso in enumerate(casos_prueba, 1):
            print(f"\n🔍 CASO {i}: {caso['descripcion']}")
            print("-" * 50)
            
            # Realizar búsqueda
            start_time = time.time()
            resultados = apis.buscar_tratamiento_pubmed(
                caso['condicion'], 
                caso['especialidad'], 
                caso['edad']
            )
            end_time = time.time()
            
            print(f"⏱️  Tiempo de búsqueda: {end_time - start_time:.2f} segundos")
            print(f"📊 Papers encontrados: {len(resultados)}")
            
            # Mostrar los primeros 5 resultados como ejemplo
            if resultados:
                print("\n📋 PRIMEROS 5 PAPERS MÁS RELEVANTES:")
                for j, paper in enumerate(resultados[:5], 1):
                    print(f"\n{j}. {paper.titulo}")
                    print(f"   📅 Año: {paper.año_publicacion}")
                    print(f"   🔗 DOI: {paper.doi}")
                    print(f"   📝 Fuente: {paper.fuente}")
                    
                    # Calcular score de relevancia
                    score = apis._calcular_score_relevancia_especifica(
                        paper, caso['condicion'], caso['especialidad']
                    )
                    print(f"   🎯 Score de relevancia: {score}")
            else:
                print("❌ No se encontraron papers relevantes")
            
            print("\n" + "="*60)
        
        print("\n✅ PRUEBA COMPLETADA")
        print("🎯 Los resultados ahora están limitados a solo 10 papers muy relevantes")
        print("📈 La relevancia se calcula basándose en:")
        print("   - Coincidencia exacta con palabras clave de la condición")
        print("   - Términos específicos de la especialidad")
        print("   - Términos de tratamiento")
        print("   - Año de publicación reciente")
        print("   - Presencia de DOI")
        print("   - Penalización por artículos de revisión o genéricos")
        
    except Exception as e:
        logger.error(f"❌ Error en la prueba: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_filtrado_papers() 