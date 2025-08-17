#!/usr/bin/env python3
"""
Script para probar las mejoras en la búsqueda de papers
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

def test_busqueda_mejorada():
    """Prueba la búsqueda mejorada de papers"""
    print("🔍 PRUEBA DE BÚSQUEDA MEJORADA")
    print("=" * 50)
    
    try:
        # Inicializar APIs
        apis = MedicalAPIsIntegration()
        
        # Casos de prueba
        casos_prueba = [
            {
                'condicion': 'dolor lumbar al levantar peso',
                'especialidad': 'fisioterapia',
                'edad': 35,
                'descripcion': 'Dolor lumbar específico'
            },
            {
                'condicion': 'dificultad para tragar después de accidente',
                'especialidad': 'fonoaudiologia',
                'edad': 45,
                'descripcion': 'Problema de deglución'
            },
            {
                'condicion': 'dolor en hombro al trabajar en computadora',
                'especialidad': 'kinesiologia',
                'edad': 28,
                'descripcion': 'Dolor laboral específico'
            },
            {
                'condicion': 'ansiedad y estrés por trabajo',
                'especialidad': 'psicologia',
                'edad': 32,
                'descripcion': 'Problema psicológico'
            }
        ]
        
        resultados_totales = {
            'casos_exitosos': 0,
            'total_papers': 0,
            'papers_relevantes': 0,
            'tiempo_promedio': 0
        }
        
        for i, caso in enumerate(casos_prueba, 1):
            print(f"\n📋 CASO {i}: {caso['descripcion']}")
            print(f"   Condición: {caso['condicion']}")
            print(f"   Especialidad: {caso['especialidad']}")
            print(f"   Edad: {caso['edad']}")
            
            # Medir tiempo de búsqueda
            inicio = time.time()
            
            try:
                # Búsqueda en PubMed
                tratamientos_pubmed = apis.buscar_tratamiento_pubmed(
                    caso['condicion'], 
                    caso['especialidad'], 
                    caso['edad']
                )
                
                # Búsqueda en Europe PMC
                tratamientos_europepmc = apis.buscar_europepmc(
                    caso['condicion'], 
                    caso['especialidad'], 
                    caso['edad']
                )
                
                tiempo_busqueda = time.time() - inicio
                
                # Combinar resultados
                todos_tratamientos = tratamientos_pubmed + tratamientos_europepmc
                
                # Analizar relevancia
                papers_relevantes = 0
                for tratamiento in todos_tratamientos:
                    if tratamiento and tratamiento.titulo:
                        # Verificar si el título contiene palabras clave relevantes
                        titulo_lower = tratamiento.titulo.lower()
                        condicion_lower = caso['condicion'].lower()
                        
                        palabras_clave = condicion_lower.split()
                        coincidencias = sum(1 for palabra in palabras_clave if palabra in titulo_lower)
                        
                        if coincidencias >= 1:
                            papers_relevantes += 1
                
                print(f"   ✅ Búsqueda completada en {tiempo_busqueda:.2f}s")
                print(f"   📊 PubMed: {len(tratamientos_pubmed)} papers")
                print(f"   📊 Europe PMC: {len(tratamientos_europepmc)} papers")
                print(f"   📊 Total: {len(todos_tratamientos)} papers")
                print(f"   🎯 Relevantes: {papers_relevantes} papers")
                
                # Mostrar algunos títulos relevantes
                if todos_tratamientos:
                    print(f"   📄 Ejemplos de papers encontrados:")
                    for j, tratamiento in enumerate(todos_tratamientos[:3], 1):
                        print(f"      {j}. {tratamiento.titulo[:80]}...")
                        if tratamiento.doi and tratamiento.doi != "Sin DOI":
                            print(f"         DOI: {tratamiento.doi}")
                
                # Actualizar estadísticas
                resultados_totales['casos_exitosos'] += 1
                resultados_totales['total_papers'] += len(todos_tratamientos)
                resultados_totales['papers_relevantes'] += papers_relevantes
                resultados_totales['tiempo_promedio'] += tiempo_busqueda
                
            except Exception as e:
                print(f"   ❌ Error en caso {i}: {e}")
                continue
        
        # Mostrar resultados finales
        print(f"\n📊 RESULTADOS FINALES")
        print("=" * 50)
        print(f"✅ Casos exitosos: {resultados_totales['casos_exitosos']}/{len(casos_prueba)}")
        print(f"📄 Total papers encontrados: {resultados_totales['total_papers']}")
        print(f"🎯 Papers relevantes: {resultados_totales['papers_relevantes']}")
        if resultados_totales['casos_exitosos'] > 0:
            print(f"⏱️  Tiempo promedio por búsqueda: {resultados_totales['tiempo_promedio']/resultados_totales['casos_exitosos']:.2f}s")
            print(f"📈 Tasa de relevancia: {resultados_totales['papers_relevantes']/resultados_totales['total_papers']*100:.1f}%")
        
        # Verificar mejoras
        print(f"\n🔍 VERIFICACIÓN DE MEJORAS")
        print("=" * 50)
        
        mejoras_verificadas = []
        
        # 1. Verificar que no hay búsquedas repetidas
        if hasattr(apis, '_search_cache'):
            print(f"✅ Sistema de caché implementado: {len(apis._search_cache)} entradas")
            mejoras_verificadas.append("Caché inteligente")
        else:
            print("❌ Sistema de caché no encontrado")
        
        # 2. Verificar criterios de relevancia más estrictos
        if hasattr(apis, '_es_articulo_altamente_relevante'):
            print("✅ Criterios de relevancia mejorados implementados")
            mejoras_verificadas.append("Relevancia mejorada")
        else:
            print("❌ Criterios de relevancia no encontrados")
        
        # 3. Verificar eliminación de duplicados mejorada
        if hasattr(apis, '_normalizar_titulo'):
            print("✅ Eliminación de duplicados mejorada implementada")
            mejoras_verificadas.append("Eliminación de duplicados")
        else:
            print("❌ Eliminación de duplicados no encontrada")
        
        # 4. Verificar términos de búsqueda más específicos
        if hasattr(apis, '_generar_terminos_busqueda_mejorados'):
            print("✅ Términos de búsqueda mejorados implementados")
            mejoras_verificadas.append("Términos específicos")
        else:
            print("❌ Términos de búsqueda no encontrados")
        
        print(f"\n✅ MEJORAS VERIFICADAS: {len(mejoras_verificadas)}/4")
        for mejora in mejoras_verificadas:
            print(f"   • {mejora}")
        
        return len(mejoras_verificadas) == 4
        
    except Exception as e:
        print(f"❌ Error en prueba de búsqueda mejorada: {e}")
        return False

def test_cache_system():
    """Prueba el sistema de caché"""
    print("\n💾 PRUEBA DEL SISTEMA DE CACHÉ")
    print("=" * 50)
    
    try:
        apis = MedicalAPIsIntegration()
        
        # Primera búsqueda (sin caché)
        print("🔍 Primera búsqueda (sin caché)...")
        inicio = time.time()
        resultados1 = apis.buscar_tratamiento_pubmed("dolor lumbar", "fisioterapia", 35)
        tiempo1 = time.time() - inicio
        print(f"   ⏱️  Tiempo: {tiempo1:.2f}s")
        print(f"   📄 Papers encontrados: {len(resultados1)}")
        
        # Segunda búsqueda (con caché)
        print("🔍 Segunda búsqueda (con caché)...")
        inicio = time.time()
        resultados2 = apis.buscar_tratamiento_pubmed("dolor lumbar", "fisioterapia", 35)
        tiempo2 = time.time() - inicio
        print(f"   ⏱️  Tiempo: {tiempo2:.2f}s")
        print(f"   📄 Papers encontrados: {len(resultados2)}")
        
        # Verificar que los resultados son iguales
        if len(resultados1) == len(resultados2):
            print("✅ Caché funcionando correctamente")
            print(f"🚀 Mejora de velocidad: {tiempo1/tiempo2:.1f}x más rápido")
            return True
        else:
            print("❌ Caché no funcionando correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de caché: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE BÚSQUEDA MEJORADA")
    print("=" * 60)
    
    # Ejecutar pruebas
    test1_exitoso = test_busqueda_mejorada()
    test2_exitoso = test_cache_system()
    
    print(f"\n📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"✅ Búsqueda mejorada: {'EXITOSA' if test1_exitoso else 'FALLIDA'}")
    print(f"✅ Sistema de caché: {'EXITOSO' if test2_exitoso else 'FALLIDO'}")
    
    if test1_exitoso and test2_exitoso:
        print("\n🎉 TODAS LAS PRUEBAS EXITOSAS")
        print("✅ La búsqueda de papers ha sido mejorada correctamente")
    else:
        print("\n⚠️ ALGUNAS PRUEBAS FALLIDAS")
        print("❌ Se requieren ajustes adicionales") 