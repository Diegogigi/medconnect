#!/usr/bin/env python3
"""
Script para probar directamente la búsqueda científica
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced


def test_busqueda_directa():
    """Prueba directamente la búsqueda científica"""

    print("🧪 Probando búsqueda científica directa...")
    print("=" * 50)

    # Crear instancia del buscador
    search_system = UnifiedScientificSearchEnhanced()

    # Casos de prueba
    casos_prueba = [
        "dolor de hombro",
        "shoulder pain",
        "dolor de rodilla",
        "knee pain",
        "rehabilitación lumbar",
        "lumbar rehabilitation",
    ]

    for i, termino in enumerate(casos_prueba, 1):
        print(f"\n{i}️⃣ Probando búsqueda: '{termino}'")
        print("-" * 50)

        try:
            # Realizar búsqueda
            evidencias = search_system.buscar_evidencia_unificada(
                termino=termino, especialidad="kinesiología", max_resultados=5
            )

            print(f"📚 Papers encontrados: {len(evidencias)}")

            if evidencias:
                # Mostrar detalles de los primeros 3 papers
                for j, paper in enumerate(evidencias[:3], 1):
                    print(f"\n📄 Paper {j}:")
                    print(f"   Título: {paper.titulo}")
                    print(f"   Autores: {', '.join(paper.autores[:3])}...")
                    print(f"   Año: {paper.año_publicacion}")
                    print(f"   Journal: {paper.journal}")
                    print(f"   DOI: {paper.doi}")
                    print(f"   Relevancia: {paper.relevancia_score:.2f}")

                    # Verificar cita APA
                    if hasattr(paper, "cita_apa") and paper.cita_apa:
                        print(f"   📖 Cita APA: {paper.cita_apa[:100]}...")
                    else:
                        print(f"   ❌ Sin cita APA")

                    # Verificar DOI
                    if paper.doi and paper.doi != "Sin DOI":
                        print(f"   ✅ DOI válido: {paper.doi}")
                    else:
                        print(f"   ❌ Sin DOI válido")

                    # Verificar relevancia del contenido
                    if (
                        "shoulder" in paper.titulo.lower()
                        or "hombro" in paper.titulo.lower()
                    ):
                        print(f"   ✅ Título relevante para hombro")
                    elif (
                        "knee" in paper.titulo.lower()
                        or "rodilla" in paper.titulo.lower()
                    ):
                        print(f"   ✅ Título relevante para rodilla")
                    elif (
                        "lumbar" in paper.titulo.lower()
                        or "lumbar" in paper.titulo.lower()
                    ):
                        print(f"   ✅ Título relevante para lumbar")
                    else:
                        print(f"   ⚠️ Título no parece relevante")
            else:
                print("❌ No se encontraron papers")

        except Exception as e:
            print(f"❌ Error en la búsqueda: {e}")

    print("\n" + "=" * 50)
    print("🎯 Prueba completada")


if __name__ == "__main__":
    test_busqueda_directa()
