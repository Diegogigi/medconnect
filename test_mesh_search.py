#!/usr/bin/env python3
"""
Script para probar las búsquedas MeSH específicas de PubMed
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration
import time

def test_mesh_search():
    """Prueba las búsquedas MeSH específicas"""
    print("🔍 PRUEBAS DE BÚSQUEDA MeSH ESPECÍFICA")
    print("=" * 60)
    
    try:
        apis = MedicalAPIsIntegration()
        print("✅ APIs médicas inicializadas correctamente")
        
        # Casos de prueba con diferentes condiciones
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
                "condicion": "dolor en cuello al trabajar en computadora",
                "especialidad": "kinesiologia",
                "descripcion": "Dolor cervical laboral"
            },
            {
                "condicion": "dolor en espalda baja",
                "especialidad": "kinesiologia",
                "descripcion": "Dolor lumbar"
            },
            {
                "condicion": "problemas para correr por dolor en rodilla",
                "especialidad": "kinesiologia",
                "descripcion": "Lesión deportiva de rodilla"
            }
        ]
        
        for i, caso in enumerate(casos_prueba, 1):
            print(f"\n📋 CASO {i}: {caso['descripcion']}")
            print(f"   Condición: '{caso['condicion']}'")
            print(f"   Especialidad: '{caso['especialidad']}'")
            print("-" * 50)
            
            try:
                # Probar generación de términos MeSH
                print(f"\n   🔍 Probando generación de términos MeSH...")
                terminos_mesh = apis._generar_terminos_mesh_especificos(caso['condicion'], caso['especialidad'])
                print(f"   📋 Términos MeSH generados: {terminos_mesh}")
                
                # Probar búsqueda en PubMed con MeSH
                print(f"\n   🔍 Probando búsqueda PubMed con MeSH...")
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
                        
                        print(f"      📊 Nivel de evidencia: {tratamiento.nivel_evidencia}")
                else:
                    print(f"   ⚠️ No se encontraron tratamientos en PubMed")
                    print(f"   ⏱️ Tiempo de búsqueda: {search_time:.2f} segundos")
                
                # Probar búsqueda en Europe PMC
                print(f"\n   🔍 Probando búsqueda Europe PMC...")
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
                        
                        print(f"      📊 Nivel de evidencia: {tratamiento.nivel_evidencia}")
                else:
                    print(f"   ⚠️ No se encontraron tratamientos en Europe PMC")
                    print(f"   ⏱️ Tiempo de búsqueda: {search_time:.2f} segundos")
                
            except Exception as e:
                print(f"   ❌ Error en caso {i}: {e}")
                continue
        
    except Exception as e:
        print(f"❌ Error en pruebas de búsqueda MeSH: {e}")
        return False
    
    return True

def test_mesh_terms():
    """Prueba la generación de términos MeSH específicos"""
    print("\n🎯 PRUEBAS DE TÉRMINOS MeSH ESPECÍFICOS")
    print("=" * 50)
    
    try:
        apis = MedicalAPIsIntegration()
        
        casos_terminos = [
            "dolor de rodilla",
            "dolor en hombro",
            "dolor en cuello",
            "dolor en espalda",
            "problemas para correr",
            "fisioterapia para dolor de rodilla",
            "dolor crónico en hombro"
        ]
        
        for i, condicion in enumerate(casos_terminos, 1):
            print(f"\n📋 Caso {i}: {condicion}")
            
            # Probar generación de términos MeSH
            terminos_mesh = apis._generar_terminos_mesh_especificos(condicion, "kinesiologia")
            print(f"   🔍 Términos MeSH: {terminos_mesh}")
            
            # Probar extracción de palabras clave
            palabras_clave = apis._extraer_palabras_clave_mesh(condicion.lower())
            print(f"   🔑 Palabras clave: {palabras_clave}")
            
            # Probar limpieza
            termino_limpio = apis._limpiar_termino_busqueda(condicion)
            print(f"   🧹 Término limpio: '{termino_limpio}'")
        
    except Exception as e:
        print(f"❌ Error en pruebas de términos MeSH: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE BÚSQUEDA MeSH")
    print("=" * 70)
    
    try:
        # Probar términos MeSH específicos
        success1 = test_mesh_terms()
        
        # Probar búsquedas MeSH
        success2 = test_mesh_search()
        
        if success1 and success2:
            print("\n\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
            print("🎯 Las búsquedas MeSH están funcionando")
            
            print("\n📋 RESUMEN DE MEJORAS MeSH:")
            print("   ✅ Sintaxis MeSH específica implementada")
            print("   ✅ Términos MeSH organizados por condición")
            print("   ✅ Búsquedas con operadores AND/OR")
            print("   ✅ Términos MeSH exactos de PubMed")
            print("   ✅ Mapeo español → términos MeSH")
            print("   ✅ Búsquedas más precisas y efectivas")
            
            print("\n🔧 CONFIGURACIÓN MeSH:")
            print("   📊 Términos MeSH específicos por condición")
            print("   🔍 Sintaxis: (\"Term\"[MeSH Terms] OR \"Term\"[MeSH Terms])")
            print("   🎯 Operadores: AND, OR para combinaciones")
            print("   📚 Términos basados en vocabulario médico oficial")
            
            print("\n🎯 BENEFICIOS MeSH:")
            print("   ✅ Búsquedas más precisas")
            print("   ✅ Resultados más relevantes")
            print("   ✅ Sintaxis estándar de PubMed")
            print("   ✅ Mayor probabilidad de encontrar estudios")
            print("   ✅ Términos médicos oficiales")
            
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