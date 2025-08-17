#!/usr/bin/env python3
"""
Script para mejorar la relevancia de búsqueda y limpiar el sistema
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced
import json


def test_search_relevance():
    """Prueba la relevancia de búsqueda con diferentes consultas"""

    search_system = UnifiedScientificSearchEnhanced()

    # Casos de prueba específicos
    test_cases = [
        {
            "query": "dolor de hombro por golpe",
            "expected_keywords": ["shoulder pain", "trauma", "contusion", "injury"],
        },
        {
            "query": "dolor de rodilla por lesión deportiva",
            "expected_keywords": [
                "knee pain",
                "sports injury",
                "trauma",
                "rehabilitation",
            ],
        },
        {
            "query": "rehabilitación post operatoria",
            "expected_keywords": [
                "postoperative rehabilitation",
                "recovery",
                "physical therapy",
            ],
        },
    ]

    print("🔍 Probando relevancia de búsqueda...")
    print("=" * 50)

    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 Caso {i}: {case['query']}")
        print("-" * 30)

        try:
            # Realizar búsqueda
            results = search_system.buscar_evidencia_unificada(case["query"])

            print(f"✅ Búsqueda completada: {len(results)} resultados")

            # Mostrar primeros 3 resultados
            for j, paper in enumerate(results[:3], 1):
                print(f"\n📄 Paper {j}:")
                print(f"   Título: {paper.titulo[:100]}...")
                print(f"   DOI: {paper.doi}")
                print(f"   Relevancia: {paper.relevancia_score}")

                # Verificar si el título contiene palabras clave esperadas
                title_lower = paper.titulo.lower()
                relevant_keywords = [
                    kw for kw in case["expected_keywords"] if kw.lower() in title_lower
                ]

                if relevant_keywords:
                    print(f"   ✅ Relevante: {relevant_keywords}")
                else:
                    print(f"   ❌ Poco relevante")

        except Exception as e:
            print(f"❌ Error en caso {i}: {e}")

    print("\n" + "=" * 50)
    print("✅ Pruebas de relevancia completadas")


def improve_search_terms():
    """Mejora los términos de búsqueda para mayor relevancia"""

    print("\n🔧 Mejorando términos de búsqueda...")

    # Mapeo de términos médicos en español a inglés más específicos
    medical_terms_mapping = {
        "dolor de hombro": [
            "shoulder pain",
            "shoulder injury",
            "shoulder trauma",
            "shoulder rehabilitation",
        ],
        "dolor de rodilla": [
            "knee pain",
            "knee injury",
            "knee trauma",
            "knee rehabilitation",
        ],
        "dolor de espalda": [
            "back pain",
            "back injury",
            "back trauma",
            "back rehabilitation",
        ],
        "golpe": ["trauma", "contusion", "injury", "impact"],
        "lesión deportiva": ["sports injury", "athletic injury", "sports trauma"],
        "rehabilitación": ["rehabilitation", "physical therapy", "recovery"],
        "post operatorio": ["postoperative", "post-surgery", "post-operative"],
        "fisioterapia": ["physical therapy", "physiotherapy", "rehabilitation"],
        "kinesiología": ["physical therapy", "kinesiology", "rehabilitation"],
    }

    print("📝 Mapeo de términos médicos:")
    for spanish, english in medical_terms_mapping.items():
        print(f"   {spanish} → {english}")

    return medical_terms_mapping


def create_improved_search_function():
    """Crea una función mejorada de búsqueda"""

    improved_function = '''
def _limpiar_termino_busqueda_mejorado(self, termino):
    """
    Versión mejorada de limpieza de términos de búsqueda
    """
    if not termino or termino.strip() == "":
        return ""
    
    # Mapeo específico de términos médicos
    medical_mapping = {
        "dolor de hombro": "shoulder pain trauma injury",
        "dolor de rodilla": "knee pain trauma injury",
        "dolor de espalda": "back pain trauma injury",
        "golpe": "trauma contusion injury impact",
        "lesión deportiva": "sports injury athletic trauma",
        "rehabilitación": "rehabilitation physical therapy recovery",
        "post operatorio": "postoperative post-surgery recovery",
        "fisioterapia": "physical therapy rehabilitation",
        "kinesiología": "physical therapy kinesiology rehabilitation"
    }
    
    termino_original = termino.lower().strip()
    
    # Aplicar mapeo médico específico
    for spanish_term, english_terms in medical_mapping.items():
        if spanish_term in termino_original:
            termino_original = termino_original.replace(spanish_term, english_terms)
    
    # Limpiar caracteres especiales y normalizar
    import re
    termino_limpio = re.sub(r'[^a-zA-Z0-9\\s]', ' ', termino_original)
    termino_limpio = re.sub(r'\\s+', ' ', termino_limpio).strip()
    
    # Asegurar que no esté vacío
    if not termino_limpio:
        return "medical rehabilitation"
    
    return termino_limpio
'''

    print("\n📝 Función mejorada de búsqueda:")
    print(improved_function)

    return improved_function


def main():
    """Función principal"""

    print("🧹 SISTEMA DE LIMPIEZA Y MEJORA DE RELEVANCIA")
    print("=" * 60)

    # 1. Probar relevancia actual
    test_search_relevance()

    # 2. Mejorar términos de búsqueda
    medical_mapping = improve_search_terms()

    # 3. Crear función mejorada
    improved_function = create_improved_search_function()

    print("\n" + "=" * 60)
    print("✅ PROCESO COMPLETADO")
    print("\n📋 Resumen de mejoras:")
    print("   1. ✅ Pruebas de relevancia ejecutadas")
    print("   2. ✅ Mapeo de términos médicos creado")
    print("   3. ✅ Función mejorada de búsqueda generada")
    print("\n🎯 Próximos pasos:")
    print("   1. Aplicar la función mejorada al sistema de búsqueda")
    print("   2. Probar con consultas específicas")
    print("   3. Verificar relevancia de resultados")


if __name__ == "__main__":
    main()
