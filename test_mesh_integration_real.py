#!/usr/bin/env python3
"""
Script para probar la integración MeSH real en el sistema de búsqueda
"""

import logging
import sys
import os

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


def test_mesh_normalization_direct():
    """Prueba la normalización MeSH directamente"""

    print("\n🔬 Probando Normalización MeSH Directa")
    print("=" * 40)

    try:
        from mesh_integration import mesh_integration

        test_terms = [
            "fisioterapia para esguince",  # Término específico que queremos probar
            "dolor de rodilla",
            "rehabilitación de hombro",
        ]

        for term in test_terms:
            print(f"\n🔍 Probando: '{term}'")

            # Normalizar término
            descriptor = mesh_integration.normalize_medical_term(term)

            if descriptor:
                print(f"   ✅ Normalizado: {descriptor.label}")
                print(f"   🔗 UI: {descriptor.ui}")
                print(f"   📚 Sinónimos: {descriptor.synonyms[:3]}")

                # Generar términos mejorados
                enhanced_terms = mesh_integration.get_enhanced_search_terms(term)
                print(f"   🔍 Términos mejorados: {enhanced_terms}")
            else:
                print(f"   ❌ No se pudo normalizar")

    except Exception as e:
        print(f"❌ Error en normalización directa: {e}")


def test_mesh_integration_in_search():
    """Prueba la integración MeSH en el sistema de búsqueda real"""

    print("🧪 Probando Integración MeSH en Sistema de Búsqueda Real")
    print("=" * 60)

    try:
        # Importar el sistema de búsqueda
        from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced

        # Crear instancia del sistema
        search_system = UnifiedScientificSearchEnhanced()

        # Probar búsqueda con término específico
        test_query = "fisioterapia para esguince"
        print(f"\n🔍 Probando búsqueda: '{test_query}'")

        # Realizar búsqueda
        resultados = search_system.buscar_evidencia_unificada(
            test_query, max_resultados=3
        )

        print(f"\n📊 Resultados obtenidos: {len(resultados)}")

        # Verificar si los resultados tienen información MeSH
        for i, resultado in enumerate(resultados):
            print(f"\n📄 Resultado {i+1}:")
            print(f"   Título: {resultado.titulo[:80]}...")
            print(f"   MeSH Terms: {getattr(resultado, 'mesh_terms', 'NO DISPONIBLE')}")
            print(
                f"   Clinical Context: {getattr(resultado, 'clinical_context', 'NO DISPONIBLE')}"
            )
            print(f"   MeSH UI: {getattr(resultado, 'mesh_ui', 'NO DISPONIBLE')}")
            print(
                f"   MeSH Synonyms: {getattr(resultado, 'mesh_synonyms', 'NO DISPONIBLE')}"
            )

            # Verificar si hay información MeSH
            if hasattr(resultado, "mesh_terms") and resultado.mesh_terms:
                print(f"   ✅ MeSH integrado: {resultado.mesh_terms}")
            else:
                print(f"   ❌ MeSH NO integrado")

        # Verificar si al menos un resultado tiene MeSH
        resultados_con_mesh = [
            r for r in resultados if hasattr(r, "mesh_terms") and r.mesh_terms
        ]

        if resultados_con_mesh:
            print(
                f"\n✅ INTEGRACIÓN MeSH FUNCIONANDO: {len(resultados_con_mesh)}/{len(resultados)} resultados tienen MeSH"
            )
        else:
            print(
                f"\n❌ INTEGRACIÓN MeSH NO FUNCIONANDO: Ningún resultado tiene información MeSH"
            )

    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Probar normalización directa
    test_mesh_normalization_direct()

    # Probar integración en búsqueda
    test_mesh_integration_in_search()

    print("\n✅ Prueba de integración MeSH completada")
