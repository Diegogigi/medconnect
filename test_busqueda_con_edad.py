#!/usr/bin/env python3
"""
Script para probar la búsqueda con consideración de edad del paciente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration

def test_busqueda_por_edad():
    """Prueba la búsqueda considerando diferentes edades"""
    print("👤 PRUEBA DE BÚSQUEDA CON CONSIDERACIÓN DE EDAD")
    print("=" * 60)
    
    apis = MedicalAPIsIntegration()
    
    # Casos de prueba con diferentes edades
    casos_prueba = [
        {
            'condicion': 'Dolor lumbar de 3 semanas',
            'especialidad': 'kinesiologia',
            'edad': 25,
            'descripcion': 'Adulto joven con dolor lumbar'
        },
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
            'condicion': 'Dificultad para tragar alimentos',
            'especialidad': 'fonoaudiologia',
            'edad': 75,
            'descripcion': 'Adulto mayor con problemas de deglución'
        },
        {
            'condicion': 'Ansiedad y estrés laboral',
            'especialidad': 'psicologia',
            'edad': 35,
            'descripcion': 'Adulto con ansiedad laboral'
        },
        {
            'condicion': 'Ansiedad y estrés laboral',
            'especialidad': 'psicologia',
            'edad': 80,
            'descripcion': 'Adulto mayor con ansiedad'
        }
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n🔍 Caso {i}: {caso['descripcion']}")
        print(f"   Condición: {caso['condicion']}")
        print(f"   Especialidad: {caso['especialidad']}")
        print(f"   Edad: {caso['edad']} años")
        print("-" * 60)
        
        try:
            resultados = apis.obtener_tratamientos_completos(
                caso['condicion'], 
                caso['especialidad'], 
                caso['edad']
            )
            
            total_pubmed = len(resultados.get('tratamientos_pubmed', []))
            total_europepmc = len(resultados.get('tratamientos_europepmc', []))
            total_preguntas = len(resultados.get('preguntas_cientificas', []))
            
            print(f"✅ Resultados PubMed: {total_pubmed}")
            print(f"✅ Resultados Europe PMC: {total_europepmc}")
            print(f"✅ Preguntas científicas: {total_preguntas}")
            print(f"✅ Total tratamientos: {total_pubmed + total_europepmc}")
            
            if total_pubmed + total_europepmc > 0:
                print("✅ Búsqueda exitosa")
                
                # Mostrar algunos resultados
                todos_tratamientos = resultados.get('tratamientos_pubmed', []) + resultados.get('tratamientos_europepmc', [])
                
                if todos_tratamientos:
                    print("\n📄 Primeros tratamientos encontrados:")
                    for j, tratamiento in enumerate(todos_tratamientos[:2], 1):
                        print(f"   {j}. {tratamiento.titulo[:80]}...")
                        print(f"      DOI: {tratamiento.doi}")
                        print(f"      Fuente: {tratamiento.fuente}")
                        print()
            else:
                print("⚠️ No se encontraron tratamientos")
                
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")

def test_terminos_por_edad():
    """Prueba la generación de términos específicos por edad"""
    print("\n👶 PRUEBA DE TÉRMINOS POR EDAD")
    print("=" * 40)
    
    apis = MedicalAPIsIntegration()
    
    # Probar diferentes edades y especialidades
    edades_prueba = [5, 15, 25, 45, 70, 85]
    especialidades_prueba = ['kinesiologia', 'fonoaudiologia', 'psicologia', 'nutricion']
    
    for edad in edades_prueba:
        print(f"\n👤 Edad: {edad} años")
        for especialidad in especialidades_prueba:
            terminos = apis._obtener_terminos_por_edad(edad, especialidad)
            print(f"   {especialidad}: {terminos[:3]}...")  # Mostrar solo los primeros 3 términos

def test_comparacion_con_sin_edad():
    """Compara resultados con y sin consideración de edad"""
    print("\n🔄 COMPARACIÓN CON Y SIN EDAD")
    print("=" * 50)
    
    apis = MedicalAPIsIntegration()
    
    # Caso de prueba
    condicion = "Dolor lumbar de 3 semanas"
    especialidad = "kinesiologia"
    edad = 70
    
    print(f"🔍 Búsqueda: '{condicion}' en '{especialidad}'")
    print(f"👤 Edad del paciente: {edad} años")
    
    # Búsqueda sin edad
    print("\n📊 SIN consideración de edad:")
    try:
        resultados_sin_edad = apis.obtener_tratamientos_completos(condicion, especialidad)
        total_sin_edad = len(resultados_sin_edad.get('tratamientos_pubmed', [])) + len(resultados_sin_edad.get('tratamientos_europepmc', []))
        print(f"   Total resultados: {total_sin_edad}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Búsqueda con edad
    print("\n📊 CON consideración de edad:")
    try:
        resultados_con_edad = apis.obtener_tratamientos_completos(condicion, especialidad, edad)
        total_con_edad = len(resultados_con_edad.get('tratamientos_pubmed', [])) + len(resultados_con_edad.get('tratamientos_europepmc', []))
        print(f"   Total resultados: {total_con_edad}")
        
        if total_con_edad > 0:
            print("   ✅ Búsqueda con edad exitosa")
            
            # Mostrar términos específicos de edad utilizados
            terminos_edad = apis._obtener_terminos_por_edad(edad, especialidad)
            print(f"   👤 Términos específicos de edad: {terminos_edad}")
        else:
            print("   ⚠️ No se encontraron resultados con edad")
            
    except Exception as e:
        print(f"   Error: {e}")

def main():
    """Función principal"""
    print("👤 PRUEBAS DE BÚSQUEDA CON CONSIDERACIÓN DE EDAD")
    print("=" * 60)
    
    # Probar términos por edad
    test_terminos_por_edad()
    
    # Probar búsqueda por edad
    test_busqueda_por_edad()
    
    # Comparar con y sin edad
    test_comparacion_con_sin_edad()
    
    print("\n✅ Todas las pruebas completadas")

if __name__ == "__main__":
    main() 