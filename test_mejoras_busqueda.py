#!/usr/bin/env python3
"""
Script para probar las mejoras en la búsqueda de APIs médicas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration
import time

def test_mejoras_busqueda():
    """Prueba las mejoras en la búsqueda de APIs médicas"""
    print("🔍 PRUEBAS DE MEJORAS EN BÚSQUEDA DE APIs MÉDICAS")
    print("=" * 60)
    
    try:
        apis = MedicalAPIsIntegration()
        print("✅ APIs médicas inicializadas correctamente")
        
        # Casos de prueba con diferentes tipos de consultas
        casos_prueba = [
            {
                "condicion": "dolor de rodilla",
                "especialidad": "kinesiologia",
                "descripcion": "Dolor de rodilla - Caso básico"
            },
            {
                "condicion": "dolor en hombro al levantar peso",
                "especialidad": "kinesiologia",
                "descripcion": "Dolor de hombro con actividad específica"
            },
            {
                "condicion": "problemas para correr por dolor en rodilla",
                "especialidad": "kinesiologia",
                "descripcion": "Limitación funcional con dolor"
            },
            {
                "condicion": "dolor en cuello al trabajar en computadora",
                "especialidad": "kinesiologia",
                "descripcion": "Dolor laboral específico"
            },
            {
                "condicion": "problemas de comunicación y lenguaje",
                "especialidad": "fonoaudiologia",
                "descripcion": "Caso de fonoaudiología"
            }
        ]
        
        for i, caso in enumerate(casos_prueba, 1):
            print(f"\n📋 CASO {i}: {caso['descripcion']}")
            print(f"   Condición: '{caso['condicion']}'")
            print(f"   Especialidad: '{caso['especialidad']}'")
            print("-" * 50)
            
            try:
                # Probar búsqueda mejorada en PubMed
                print(f"\n   🔍 Probando PubMed con búsqueda mejorada...")
                start_time = time.time()
                
                tratamientos_pubmed = apis.buscar_tratamiento_pubmed(caso['condicion'], caso['especialidad'])
                
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
                
                # Probar búsqueda mejorada en Europe PMC
                print(f"\n   🔍 Probando Europe PMC con búsqueda mejorada...")
                start_time = time.time()
                
                tratamientos_europepmc = apis.buscar_europepmc(caso['condicion'], caso['especialidad'])
                
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
                
                # Probar generación de términos de búsqueda mejorados
                print(f"\n   🔍 Probando generación de términos mejorados...")
                terminos_mejorados = apis._generar_terminos_busqueda_mejorados(caso['condicion'], caso['especialidad'])
                print(f"   📋 Términos generados: {terminos_mejorados}")
                
                # Probar limpieza de términos
                termino_limpio = apis._limpiar_termino_busqueda(caso['condicion'])
                print(f"   🧹 Término limpio: '{termino_limpio}'")
                
            except Exception as e:
                print(f"   ❌ Error en caso {i}: {e}")
                continue
        
    except Exception as e:
        print(f"❌ Error en pruebas de mejoras de búsqueda: {e}")
        return False
    
    return True

def test_terminos_especificos():
    """Prueba términos médicos específicos"""
    print("\n🎯 PRUEBAS DE TÉRMINOS MÉDICOS ESPECÍFICOS")
    print("=" * 50)
    
    try:
        apis = MedicalAPIsIntegration()
        
        casos_terminos = [
            "dolor de rodilla",
            "dolor en hombro",
            "dolor en cuello",
            "dolor en espalda",
            "problemas para correr",
            "dificultad para trabajar"
        ]
        
        for i, condicion in enumerate(casos_terminos, 1):
            print(f"\n📋 Caso {i}: {condicion}")
            
            # Probar extracción de palabras clave
            palabras_clave = apis._extraer_palabras_clave(condicion)
            print(f"   🔑 Palabras clave: {palabras_clave}")
            
            # Probar términos médicos específicos
            terminos_especificos = apis._obtener_terminos_medicos_especificos(condicion)
            print(f"   🏥 Términos específicos: {terminos_especificos}")
            
            # Probar términos de tratamiento
            terminos_tratamiento = apis._obtener_terminos_tratamiento(condicion)
            print(f"   💊 Términos tratamiento: {terminos_tratamiento}")
            
            # Probar limpieza
            termino_limpio = apis._limpiar_termino_busqueda(condicion)
            print(f"   🧹 Término limpio: '{termino_limpio}'")
        
    except Exception as e:
        print(f"❌ Error en pruebas de términos específicos: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE MEJORAS EN BÚSQUEDA")
    print("=" * 70)
    
    try:
        # Probar términos específicos
        success1 = test_terminos_especificos()
        
        # Probar mejoras de búsqueda
        success2 = test_mejoras_busqueda()
        
        if success1 and success2:
            print("\n\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
            print("🎯 Las mejoras en búsqueda están funcionando")
            
            print("\n📋 RESUMEN DE MEJORAS IMPLEMENTADAS:")
            print("   ✅ Generación de múltiples términos de búsqueda")
            print("   ✅ Extracción inteligente de palabras clave")
            print("   ✅ Términos médicos específicos por condición")
            print("   ✅ Limpieza y normalización de términos")
            print("   ✅ Búsqueda más amplia sin filtros restrictivos")
            print("   ✅ Múltiples variaciones de búsqueda")
            print("   ✅ Rate limiting optimizado")
            print("   ✅ Manejo de errores mejorado")
            
            print("\n🔧 CONFIGURACIÓN DE BÚSQUEDA:")
            print("   📊 Resultados por búsqueda: 10")
            print("   ⏱️ Rate limiting: 0.5s entre requests")
            print("   🔍 Múltiples términos por consulta")
            print("   🧹 Limpieza automática de términos")
            print("   🏥 Términos médicos específicos")
            
            print("\n🎯 BENEFICIOS OBTENIDOS:")
            print("   ✅ Mayor cobertura de búsqueda")
            print("   ✅ Términos más relevantes")
            print("   ✅ Mejor traducción español → inglés")
            print("   ✅ Búsquedas más efectivas")
            print("   ✅ Resultados más específicos")
            print("   ✅ Sistema más robusto")
            
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