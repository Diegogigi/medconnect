#!/usr/bin/env python3
"""
Script para probar la búsqueda personalizada con selección de términos por el profesional
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration

def test_generar_terminos_disponibles():
    """Prueba la generación de términos disponibles para selección"""
    print("🔍 PRUEBA DE GENERACIÓN DE TÉRMINOS DISPONIBLES")
    print("=" * 60)
    
    apis = MedicalAPIsIntegration()
    
    # Casos de prueba
    casos_prueba = [
        {
            'condicion': 'Dolor lumbar de 3 semanas',
            'especialidad': 'kinesiologia',
            'edad': 70,
            'descripcion': 'Adulto mayor con dolor lumbar'
        },
        {
            'condicion': 'Dificultad para tragar alimentos',
            'especialidad': 'fonoaudiologia',
            'edad': 8,
            'descripcion': 'Niño con problemas de deglución'
        },
        {
            'condicion': 'Ansiedad y estrés laboral',
            'especialidad': 'psicologia',
            'edad': 35,
            'descripcion': 'Adulto con ansiedad laboral'
        }
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n🔍 Caso {i}: {caso['descripcion']}")
        print(f"   Condición: {caso['condicion']}")
        print(f"   Especialidad: {caso['especialidad']}")
        print(f"   Edad: {caso['edad']} años")
        print("-" * 60)
        
        try:
            terminos_disponibles = apis.generar_terminos_busqueda_disponibles(
                caso['condicion'], 
                caso['especialidad'], 
                caso['edad']
            )
            
            print("📋 TÉRMINOS DISPONIBLES:")
            
            # Términos básicos
            print(f"\n🔤 Términos básicos ({len(terminos_disponibles['terminos_basicos'])}):")
            for j, termino in enumerate(terminos_disponibles['terminos_basicos'], 1):
                print(f"   {j}. {termino}")
            
            # Términos de especialidad
            print(f"\n🏥 Términos de especialidad ({len(terminos_disponibles['terminos_especialidad'])}):")
            for j, termino in enumerate(terminos_disponibles['terminos_especialidad'], 1):
                print(f"   {j}. {termino}")
            
            # Términos por edad
            if terminos_disponibles['terminos_edad']:
                print(f"\n👤 Términos por edad ({len(terminos_disponibles['terminos_edad'])}):")
                for j, termino in enumerate(terminos_disponibles['terminos_edad'], 1):
                    print(f"   {j}. {termino}")
            
            # Términos combinados
            print(f"\n🔗 Términos combinados ({len(terminos_disponibles['terminos_combinados'])}):")
            for j, termino in enumerate(terminos_disponibles['terminos_combinados'][:5], 1):
                print(f"   {j}. {termino}")
            
            # Términos recomendados
            print(f"\n⭐ Términos recomendados ({len(terminos_disponibles['terminos_recomendados'])}):")
            for j, termino in enumerate(terminos_disponibles['terminos_recomendados'], 1):
                print(f"   {j}. {termino}")
                
        except Exception as e:
            print(f"❌ Error generando términos: {e}")

def test_busqueda_con_terminos_seleccionados():
    """Prueba la búsqueda con términos seleccionados por el profesional"""
    print("\n👨‍⚕️ PRUEBA DE BÚSQUEDA CON TÉRMINOS SELECCIONADOS")
    print("=" * 60)
    
    apis = MedicalAPIsIntegration()
    
    # Caso de prueba
    condicion = "Dolor lumbar de 3 semanas"
    especialidad = "kinesiologia"
    edad = 70
    
    print(f"🔍 Caso: {condicion}")
    print(f"🏥 Especialidad: {especialidad}")
    print(f"👤 Edad: {edad} años")
    
    # Generar términos disponibles
    terminos_disponibles = apis.generar_terminos_busqueda_disponibles(condicion, especialidad, edad)
    
    # Simular selección del profesional
    terminos_seleccionados = [
        "geriatric rehabilitation",
        "elderly physical therapy", 
        "back pain",
        "rehabilitation"
    ]
    
    print(f"\n👨‍⚕️ Términos seleccionados por el profesional: {terminos_seleccionados}")
    print("-" * 60)
    
    try:
        # Realizar búsqueda con términos personalizados
        resultados = apis.buscar_con_terminos_personalizados(
            condicion, 
            especialidad, 
            terminos_seleccionados, 
            edad
        )
        
        total_pubmed = len(resultados.get('tratamientos_pubmed', []))
        total_europepmc = len(resultados.get('tratamientos_europepmc', []))
        total_preguntas = len(resultados.get('preguntas_cientificas', []))
        
        print(f"✅ Resultados PubMed: {total_pubmed}")
        print(f"✅ Resultados Europe PMC: {total_europepmc}")
        print(f"✅ Preguntas científicas: {total_preguntas}")
        print(f"✅ Total tratamientos: {total_pubmed + total_europepmc}")
        
        if total_pubmed + total_europepmc > 0:
            print("✅ Búsqueda personalizada exitosa")
            
            # Mostrar algunos resultados
            todos_tratamientos = resultados.get('tratamientos_pubmed', []) + resultados.get('tratamientos_europepmc', [])
            
            if todos_tratamientos:
                print("\n📄 Primeros tratamientos encontrados:")
                for j, tratamiento in enumerate(todos_tratamientos[:3], 1):
                    print(f"   {j}. {tratamiento.titulo[:80]}...")
                    print(f"      DOI: {tratamiento.doi}")
                    print(f"      Fuente: {tratamiento.fuente}")
                    print()
        else:
            print("⚠️ No se encontraron tratamientos con términos personalizados")
            
    except Exception as e:
        print(f"❌ Error en búsqueda personalizada: {e}")

def test_comparacion_busquedas():
    """Compara búsqueda automática vs búsqueda personalizada"""
    print("\n🔄 COMPARACIÓN DE BÚSQUEDAS")
    print("=" * 50)
    
    apis = MedicalAPIsIntegration()
    
    # Caso de prueba
    condicion = "Dolor lumbar de 3 semanas"
    especialidad = "kinesiologia"
    edad = 70
    
    print(f"🔍 Caso: {condicion}")
    print(f"🏥 Especialidad: {especialidad}")
    print(f"👤 Edad: {edad} años")
    
    # Búsqueda automática
    print("\n📊 BÚSQUEDA AUTOMÁTICA:")
    try:
        resultados_auto = apis.obtener_tratamientos_completos(condicion, especialidad, edad)
        total_auto = len(resultados_auto.get('tratamientos_pubmed', [])) + len(resultados_auto.get('tratamientos_europepmc', []))
        print(f"   Total resultados: {total_auto}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Búsqueda personalizada
    print("\n📊 BÚSQUEDA PERSONALIZADA:")
    terminos_seleccionados = ["geriatric rehabilitation", "elderly physical therapy", "back pain"]
    print(f"   Términos seleccionados: {terminos_seleccionados}")
    
    try:
        resultados_personalizada = apis.buscar_con_terminos_personalizados(
            condicion, especialidad, terminos_seleccionados, edad
        )
        total_personalizada = len(resultados_personalizada.get('tratamientos_pubmed', [])) + len(resultados_personalizada.get('tratamientos_europepmc', []))
        print(f"   Total resultados: {total_personalizada}")
        
        if total_personalizada > 0:
            print("   ✅ Búsqueda personalizada exitosa")
        else:
            print("   ⚠️ No se encontraron resultados")
            
    except Exception as e:
        print(f"   Error: {e}")

def test_interfaz_simulada():
    """Simula la interfaz de selección de términos"""
    print("\n🖥️ SIMULACIÓN DE INTERFAZ DE SELECCIÓN")
    print("=" * 50)
    
    apis = MedicalAPIsIntegration()
    
    # Caso de prueba
    condicion = "Dificultad para tragar alimentos"
    especialidad = "fonoaudiologia"
    edad = 8
    
    print(f"🔍 Condición: {condicion}")
    print(f"🏥 Especialidad: {especialidad}")
    print(f"👤 Edad: {edad} años")
    
    # Generar términos disponibles
    terminos_disponibles = apis.generar_terminos_busqueda_disponibles(condicion, especialidad, edad)
    
    print("\n📋 TÉRMINOS DISPONIBLES PARA SELECCIÓN:")
    print("(Simulando interfaz donde el profesional puede seleccionar)")
    
    # Mostrar términos recomendados
    print(f"\n⭐ Términos recomendados ({len(terminos_disponibles['terminos_recomendados'])}):")
    for i, termino in enumerate(terminos_disponibles['terminos_recomendados'], 1):
        print(f"   [ ] {i}. {termino}")
    
    # Simular selección del profesional
    seleccion_simulada = [1, 3, 5]  # Índices seleccionados
    terminos_seleccionados = [terminos_disponibles['terminos_recomendados'][i-1] for i in seleccion_simulada]
    
    print(f"\n👨‍⚕️ Selección simulada del profesional: {terminos_seleccionados}")
    
    # Realizar búsqueda con términos seleccionados
    try:
        resultados = apis.buscar_con_terminos_personalizados(
            condicion, especialidad, terminos_seleccionados, edad
        )
        
        total_resultados = len(resultados.get('tratamientos_pubmed', [])) + len(resultados.get('tratamientos_europepmc', []))
        print(f"\n✅ Búsqueda completada: {total_resultados} tratamientos encontrados")
        
        if total_resultados > 0:
            print("✅ Búsqueda personalizada exitosa")
        else:
            print("⚠️ No se encontraron tratamientos")
            
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")

def main():
    """Función principal"""
    print("👨‍⚕️ PRUEBAS DE BÚSQUEDA PERSONALIZADA")
    print("=" * 60)
    
    # Probar generación de términos disponibles
    test_generar_terminos_disponibles()
    
    # Probar búsqueda con términos seleccionados
    test_busqueda_con_terminos_seleccionados()
    
    # Comparar búsquedas
    test_comparacion_busquedas()
    
    # Simular interfaz
    test_interfaz_simulada()
    
    print("\n✅ Todas las pruebas completadas")

if __name__ == "__main__":
    main() 