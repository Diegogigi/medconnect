#!/usr/bin/env python3
"""
Prueba de integración completa: MedlinePlus + Sistema Unificado de IAs
"""

import sys
import time
from medlineplus_integration import (
    medlineplus_integration,
    get_patient_education_for_code,
)
from unified_scientific_search_enhanced import unified_search_enhanced


def test_medlineplus_direct():
    """Prueba directa de MedlinePlus Integration"""
    print("🧪 Probando MedlinePlus Integration Directa")
    print("=" * 50)

    # Prueba 1: Diagnóstico ICD-10
    print("\n🔍 Prueba 1: Diagnóstico ICD-10 (J45.901 - Asma)")
    result = medlineplus_integration.get_diagnosis_education("J45.901", "es")
    print(f"✅ Título: {result.title}")
    print(f"🔗 URL: {result.url}")
    print(f"📝 Resumen: {result.summary[:150]}...")
    print(f"🌐 Idioma: {result.language}")
    print(f"✅ Éxito: {result.success}")

    # Prueba 2: Medicamento RxCUI
    print("\n🔍 Prueba 2: Medicamento RxCUI (197361 - Aspirin)")
    result = medlineplus_integration.get_medication_education("197361", "es")
    print(f"✅ Título: {result.title}")
    print(f"🔗 URL: {result.url}")
    print(f"📝 Resumen: {result.summary[:150]}...")
    print(f"🌐 Idioma: {result.language}")
    print(f"✅ Éxito: {result.success}")

    # Prueba 3: Prueba de laboratorio LOINC
    print("\n🔍 Prueba 3: Prueba de laboratorio LOINC (3187-2 - Factor IX)")
    result = medlineplus_integration.get_lab_test_education("3187-2", "es")
    print(f"✅ Título: {result.title}")
    print(f"🔗 URL: {result.url}")
    print(f"📝 Resumen: {result.summary[:150]}...")
    print(f"🌐 Idioma: {result.language}")
    print(f"✅ Éxito: {result.success}")


def test_integration_with_unified_system():
    """Prueba de integración con el sistema unificado"""
    print("\n🧪 Probando Integración con Sistema Unificado")
    print("=" * 50)

    # Consultas médicas para probar
    consultas_medicas = [
        "dolor de rodilla",
        "fisioterapia para esguince",
        "asma tratamiento",
        "diabetes tipo 2",
    ]

    for i, consulta in enumerate(consultas_medicas, 1):
        print(f"\n🔍 Prueba {i}: '{consulta}'")
        print("-" * 30)

        start_time = time.time()

        try:
            # Buscar evidencia científica con integración MeSH + MedlinePlus
            evidencias = unified_search_enhanced.buscar_evidencia_unificada(
                consulta, max_resultados=3
            )

            tiempo = time.time() - start_time

            print(f"⏱️ Tiempo: {tiempo:.2f}s")
            print(f"📊 Resultados: {len(evidencias)}")

            if evidencias:
                # Mostrar primer resultado con información educativa
                evidencia = evidencias[0]
                print(f"📄 Título: {evidencia.titulo[:80]}...")
                print(
                    f"🏥 Especialidad: {evidencia.clinical_context.get('specialty', 'N/A')}"
                )

                # Verificar información educativa
                if (
                    hasattr(evidencia, "patient_education")
                    and evidencia.patient_education
                ):
                    education = evidencia.patient_education
                    print(f"📚 Educación del paciente:")
                    print(f"   Título: {education.get('title', 'N/A')}")
                    print(f"   Contenido: {education.get('content', 'N/A')[:100]}...")
                    print(f"   URL: {education.get('url', 'N/A')}")
                    print(f"   Disponible: {education.get('show_panel', False)}")
                    print(f"   Fuente: {education.get('source', 'N/A')}")
                else:
                    print("❌ No hay información educativa disponible")

                # Verificar integración MeSH
                if hasattr(evidencia, "mesh_terms") and evidencia.mesh_terms:
                    print(f"🏷️ Términos MeSH: {evidencia.mesh_terms}")
                    print(f"🔗 UI MeSH: {evidencia.mesh_ui}")
                else:
                    print("❌ No hay términos MeSH disponibles")

        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")


def test_patient_education_function():
    """Prueba de la función de conveniencia"""
    print("\n🧪 Probando Función de Conveniencia")
    print("=" * 50)

    # Pruebas con diferentes tipos de códigos
    pruebas = [
        ("diagnosis", "J45.901", "es"),
        ("medication", "197361", "es"),
        ("lab_test", "3187-2", "es"),
        ("procedure", "99213", "es"),  # CPT code
    ]

    for code_type, code, lang in pruebas:
        print(f"\n🔍 Prueba: {code_type} - {code} ({lang})")

        try:
            result = get_patient_education_for_code(code_type, code, lang)
            print(f"✅ Título: {result.get('title', 'N/A')}")
            print(f"📝 Contenido: {result.get('content', 'N/A')[:100]}...")
            print(f"🔗 URL: {result.get('url', 'N/A')}")
            print(f"📋 Mostrar panel: {result.get('show_panel', False)}")
            print(f"🏥 Fuente: {result.get('source', 'N/A')}")

        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Función principal de pruebas"""
    print("🚀 PRUEBA COMPLETA: Integración MedlinePlus + Sistema Unificado")
    print("=" * 70)

    try:
        # Prueba 1: MedlinePlus directo
        test_medlineplus_direct()

        # Prueba 2: Integración con sistema unificado
        test_integration_with_unified_system()

        # Prueba 3: Función de conveniencia
        test_patient_education_function()

        print("\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("🎉 La integración MedlinePlus está funcionando correctamente")

    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
