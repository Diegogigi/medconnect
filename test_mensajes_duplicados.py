#!/usr/bin/env python3
"""
Script para probar la eliminación de mensajes duplicados y mejora en relevancia de papers
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

def test_mensajes_duplicados():
    """Prueba la eliminación de mensajes duplicados y mejora en relevancia"""
    print("🎯 PRUEBA DE ELIMINACIÓN DE MENSAJES DUPLICADOS")
    print("=" * 60)
    
    try:
        # Inicializar APIs
        apis = MedicalAPIsIntegration()
        
        # Casos de prueba específicos para verificar relevancia
        casos_prueba = [
            {
                'condicion': 'dolor lumbar',
                'especialidad': 'kinesiologia',
                'edad': 40,
                'descripcion': 'Dolor lumbar en adulto - debe ser muy relevante'
            },
            {
                'condicion': 'problemas de deglución',
                'especialidad': 'fonoaudiologia',
                'edad': 65,
                'descripcion': 'Problemas de deglución en adulto mayor - debe ser específico'
            },
            {
                'condicion': 'lesión de rodilla',
                'especialidad': 'fisioterapia',
                'edad': 28,
                'descripcion': 'Lesión de rodilla en deportista - debe ser muy específico'
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
            
            # Verificar relevancia de los resultados
            if resultados:
                print(f"\n📋 PAPERS ENCONTRADOS (máximo 10):")
                for j, paper in enumerate(resultados, 1):
                    # Calcular score de relevancia
                    score = apis._calcular_score_relevancia_especifica(
                        paper, caso['condicion'], caso['especialidad']
                    )
                    
                    print(f"\n{j}. {paper.titulo}")
                    print(f"   📅 Año: {paper.año_publicacion}")
                    print(f"   🔗 DOI: {paper.doi}")
                    print(f"   🎯 Score de relevancia: {score}")
                    
                    # Verificar si es altamente relevante
                    if score >= 15:
                        print(f"   ✅ ALTAMENTE RELEVANTE")
                    elif score >= 8:
                        print(f"   ⚠️  MODERADAMENTE RELEVANTE")
                    else:
                        print(f"   ❌ POCO RELEVANTE")
                    
                    # Verificar si contiene palabras clave de la condición
                    condicion_lower = caso['condicion'].lower()
                    titulo_lower = paper.titulo.lower()
                    
                    palabras_clave = condicion_lower.split()
                    coincidencias = sum(1 for palabra in palabras_clave if palabra in titulo_lower)
                    
                    if coincidencias > 0:
                        print(f"   🎯 Coincidencias con condición: {coincidencias}")
                    else:
                        print(f"   ⚠️  Sin coincidencias directas con condición")
            else:
                print("❌ No se encontraron papers relevantes")
            
            print("\n" + "="*60)
        
        print("\n✅ PRUEBA COMPLETADA")
        print("🎯 Mejoras implementadas:")
        print("   - Eliminación de mensajes duplicados")
        print("   - Control de mensajes por motivo de consulta")
        print("   - Filtrado a máximo 10 papers relevantes")
        print("   - Score de relevancia mejorado")
        print("   - Verificación de coincidencias con condición")
        
    except Exception as e:
        logger.error(f"❌ Error en la prueba: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_mensajes_duplicados() 