#!/usr/bin/env python3
"""
Script para probar directamente la búsqueda científica
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced


def test_busqueda_cientifica():
    """Prueba la búsqueda científica directamente"""

    print("🧪 Probando búsqueda científica directamente...")
    print("=" * 50)

    # Inicializar sistema de búsqueda
    search_system = UnifiedScientificSearchEnhanced()

    # Casos de prueba
    casos_prueba = [
        "dolor de hombro por golpe en el trabajo",
        "shoulder pain trauma work injury",
        "kinesiología rehabilitación hombro",
        "physical therapy shoulder rehabilitation",
        "dolor lumbar postraumático",
        "low back pain trauma",
    ]

    for i, consulta in enumerate(casos_prueba, 1):
        print(f"\n{i}️⃣ Probando consulta: '{consulta}'")
        print("-" * 40)

        try:
            # Realizar búsqueda
            resultados = search_system.buscar_evidencia_unificada(
                consulta, max_resultados=3
            )

            print(f"✅ Búsqueda completada: {len(resultados)} resultados")

            if resultados:
                for j, paper in enumerate(resultados, 1):
                    print(f"\n📄 Paper {j}:")
                    print(f"   Título: {paper.titulo}")
                    print(f"   Autores: {', '.join(paper.autores[:3])}")
                    print(f"   Año: {paper.año_publicacion}")
                    print(f"   DOI: {paper.doi}")
                    print(f"   Relevancia: {paper.relevancia_score:.2f}")
                    print(f"   Fuente: {paper.fuente}")
                    print(f"   Resumen: {paper.resumen[:100]}...")
            else:
                print("❌ No se encontraron resultados")

        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")

    print("\n" + "=" * 50)
    print("🎯 Prueba completada")


if __name__ == "__main__":
    test_busqueda_cientifica()
