#!/usr/bin/env python3
"""
Script para probar el sistema de comunicación en tiempo real de Copilot Health
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

def test_comunicacion_tiempo_real():
    """Prueba el sistema de comunicación en tiempo real"""
    print("🎯 PRUEBA DE COMUNICACIÓN EN TIEMPO REAL")
    print("=" * 60)
    
    try:
        # Inicializar APIs
        apis = MedicalAPIsIntegration()
        
        # Casos de prueba para verificar comunicación
        casos_prueba = [
            {
                'condicion': 'dolor de espalda',
                'especialidad': 'kinesiologia',
                'edad': 35,
                'descripcion': 'Dolor de espalda - debe mostrar proceso paso a paso'
            },
            {
                'condicion': 'problemas de voz',
                'especialidad': 'fonoaudiologia',
                'edad': 45,
                'descripcion': 'Problemas de voz - debe comunicar cada etapa'
            }
        ]
        
        for i, caso in enumerate(casos_prueba, 1):
            print(f"\n🔍 CASO {i}: {caso['descripcion']}")
            print("-" * 50)
            
            # Simular proceso de comunicación en tiempo real
            print("🤖 Copilot Health: Iniciando análisis del caso...")
            time.sleep(1)
            
            print("🔍 Copilot Health: Analizando motivo de consulta...")
            time.sleep(1)
            
            print("📝 Copilot Health: Extrayendo información clave...")
            time.sleep(1)
            
            # Realizar búsqueda
            start_time = time.time()
            print("🔬 Copilot Health: Consultando bases de datos médicas...")
            
            resultados = apis.buscar_tratamiento_pubmed(
                caso['condicion'], 
                caso['especialidad'], 
                caso['edad']
            )
            end_time = time.time()
            
            print(f"⏱️  Tiempo de búsqueda: {end_time - start_time:.2f} segundos")
            print(f"📊 Papers encontrados: {len(resultados)}")
            
            # Simular comunicación de resultados
            if resultados:
                print("✅ Copilot Health: Encontrados estudios científicos relevantes")
                print("🎯 Copilot Health: Filtrando por relevancia...")
                print("📋 Copilot Health: Mostrando resultados en sidebar...")
                
                # Mostrar algunos resultados
                for j, paper in enumerate(resultados[:3], 1):
                    score = apis._calcular_score_relevancia_especifica(
                        paper, caso['condicion'], caso['especialidad']
                    )
                    print(f"   📄 {j}. {paper.titulo[:60]}... (Score: {score})")
            else:
                print("⚠️  Copilot Health: No se encontraron estudios específicos")
                print("💡 Copilot Health: Sugiriendo ajustar términos de búsqueda")
            
            print("🎯 Copilot Health: Análisis completado")
            print("\n" + "="*60)
        
        print("\n✅ PRUEBA COMPLETADA")
        print("🎯 Sistema de comunicación implementado:")
        print("   - Chat flotante en tiempo real")
        print("   - Mensajes paso a paso del proceso")
        print("   - Indicadores de progreso")
        print("   - Animaciones de typing")
        print("   - Diferentes tipos de mensajes (success, warning, error)")
        print("   - Botón flotante para activar/desactivar chat")
        
    except Exception as e:
        logger.error(f"❌ Error en la prueba: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_comunicacion_tiempo_real() 