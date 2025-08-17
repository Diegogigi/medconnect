#!/usr/bin/env python3
"""
Script para probar la generación de DOIs y citas APA
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_scientific_search_enhanced import (
    UnifiedScientificSearchEnhanced,
    APACitationFormatter,
)


def test_doi_apa_citations():
    """Prueba la generación de DOIs y citas APA"""

    print("🧪 Probando generación de DOIs y citas APA...")
    print("=" * 50)

    # Inicializar sistema de búsqueda
    search_system = UnifiedScientificSearchEnhanced()

    # Casos de prueba
    casos_prueba = [
        "dolor de rodilla por lesión al jugar futbol",
        "shoulder pain trauma work injury",
        "low back pain physical therapy",
        "knee injury rehabilitation",
    ]

    for i, consulta in enumerate(casos_prueba, 1):
        print(f"\n{i}️⃣ Probando consulta: '{consulta}'")
        print("-" * 50)

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

                    # Verificar cita APA
                    if paper.cita_apa:
                        print(f"   📖 Cita APA: {paper.cita_apa}")
                    else:
                        print(f"   ❌ Sin cita APA")

                    # Verificar DOI
                    if paper.doi and paper.doi != "Sin DOI":
                        print(f"   ✅ DOI válido: {paper.doi}")
                    else:
                        print(f"   ❌ Sin DOI válido")

                    print(f"   📝 Resumen: {paper.resumen[:100]}...")
            else:
                print("❌ No se encontraron resultados")

        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")

    print("\n" + "=" * 50)

    # Probar formateador APA directamente
    print("🧪 Probando formateador APA directamente...")

    from dataclasses import dataclass

    @dataclass
    class MockEvidencia:
        titulo: str
        autores: list
        año_publicacion: str
        journal: str
        volumen: str
        numero: str
        paginas: str
        doi: str

    # Casos de prueba para APA
    casos_apa = [
        MockEvidencia(
            titulo="Effectiveness of physical therapy for knee pain",
            autores=["Smith, J.", "Johnson, A.", "Brown, M."],
            año_publicacion="2023",
            journal="Journal of Physical Therapy",
            volumen="15",
            numero="2",
            paginas="45-52",
            doi="10.1234/jpt.2023.001",
        ),
        MockEvidencia(
            titulo="Rehabilitation protocols for shoulder injuries",
            autores=["García, L."],
            año_publicacion="2022",
            journal="Sports Medicine",
            volumen="",
            numero="",
            paginas="",
            doi="",
        ),
    ]

    for i, evidencia in enumerate(casos_apa, 1):
        print(f"\n📖 Caso APA {i}:")
        cita = APACitationFormatter.format_citation(evidencia)
        print(f"   Cita generada: {cita}")

    print("\n" + "=" * 50)
    print("🎯 Prueba completada")


if __name__ == "__main__":
    test_doi_apa_citations()
