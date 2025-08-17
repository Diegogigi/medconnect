#!/usr/bin/env python3
"""
Script de prueba específico para el caso de dolor de rodilla
"""

import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_caso_rodilla():
    """Prueba específica para el caso de dolor de rodilla"""

    print("🧪 Probando caso específico: Dolor de rodilla por golpe en el trabajo")
    print("=" * 70)

    # Caso específico del usuario
    consulta_original = (
        "USUARIA LLEGA A LA CONSULTA CON DOLOR EN LA RODILLA POR GOLPE EN EL TRABAJO"
    )

    try:
        # 1. Probar procesamiento NLP
        print("1️⃣ Procesamiento NLP...")
        from unified_nlp_processor_main import UnifiedNLPProcessor

        nlp_processor = UnifiedNLPProcessor()
        analisis_completo = nlp_processor.procesar_consulta_completa(consulta_original)

        print(f"   ✅ NLP completado")
        print(
            f"   📝 Síntomas: {[s.sintoma for s in analisis_completo.consulta_procesada.sintomas]}"
        )
        print(
            f"   🏥 Entidades: {[e.texto for e in analisis_completo.consulta_procesada.entidades_clinicas]}"
        )
        print(f"   📊 Confianza: {analisis_completo.confianza_global}")

        # 2. Probar limpieza de términos
        print("\n2️⃣ Limpieza de términos de búsqueda...")
        from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced

        search_system = UnifiedScientificSearchEnhanced()
        termino_limpio = search_system._limpiar_termino_busqueda(consulta_original)
        print(f"   🔍 Término original: {consulta_original}")
        print(f"   🔍 Término limpio: {termino_limpio}")

        # 3. Probar generación de términos generales
        print("\n3️⃣ Generación de términos generales...")
        termino_general = search_system._generar_terminos_generales(consulta_original)
        print(f"   🔍 Término general: {termino_general}")

        # 4. Probar búsqueda científica
        print("\n4️⃣ Búsqueda científica...")
        resultados = search_system.buscar_evidencia_unificada(
            consulta_original, max_resultados=5
        )

        print(f"   ✅ Búsqueda completada - {len(resultados)} resultados")

        if resultados:
            print("\n   📚 Resultados encontrados:")
            for i, evidencia in enumerate(resultados, 1):
                print(f"   {i}. {evidencia.titulo[:80]}...")
                print(f"      📊 Score: {evidencia.relevancia_score:.2f}")
                print(f"      📅 Año: {evidencia.año_publicacion}")
                print(f"      🔗 DOI: {evidencia.doi}")
                print(f"      📝 Fuente: {evidencia.fuente}")
                print()
        else:
            print("   ⚠️ No se encontraron resultados específicos")

            # Probar búsquedas alternativas
            print("\n   🔄 Probando búsquedas alternativas...")

            terminos_alternativos = [
                "knee pain treatment",
                "knee injury physical therapy",
                "knee trauma rehabilitation",
                "musculoskeletal pain treatment",
                "physical therapy guidelines",
            ]

            for termino_alt in terminos_alternativos:
                print(f"   🔍 Probando: {termino_alt}")
                resultados_alt = search_system.buscar_evidencia_unificada(
                    termino_alt, max_resultados=3
                )
                if resultados_alt:
                    print(f"      ✅ Encontrados: {len(resultados_alt)} resultados")
                    for ev in resultados_alt[:1]:
                        print(f"      📚 {ev.titulo[:60]}...")
                    break
                else:
                    print(f"      ❌ Sin resultados")

        # 5. Probar análisis clínico
        print("\n5️⃣ Análisis clínico...")
        from unified_copilot_assistant_enhanced import UnifiedCopilotAssistantEnhanced

        copilot = UnifiedCopilotAssistantEnhanced()

        # Convertir evidencias al formato esperado
        chunks_evidencia = []
        for ev in resultados:
            from unified_copilot_assistant_enhanced import ChunkEvidencia

            chunk = ChunkEvidencia(
                texto=ev.resumen,
                fuente=ev.fuente,
                doi=ev.doi,
                autores=ev.autores,
                año=ev.año_publicacion,
                titulo=ev.titulo,
                seccion="abstract",
                inicio_char=0,
                fin_char=len(ev.resumen),
                relevancia_score=ev.relevancia_score,
            )
            chunks_evidencia.append(chunk)

        # Si no hay evidencias, crear una ficticia para el análisis
        if not chunks_evidencia:
            from unified_copilot_assistant_enhanced import ChunkEvidencia

            chunk_ficticio = ChunkEvidencia(
                texto="Knee pain treatment typically involves physical therapy, exercise, and pain management techniques.",
                fuente="clinical_guidelines",
                doi="",
                autores=["Clinical Guidelines"],
                año="2024",
                titulo="Knee Pain Treatment Guidelines",
                seccion="guidelines",
                inicio_char=0,
                fin_char=100,
                relevancia_score=0.8,
            )
            chunks_evidencia.append(chunk_ficticio)

        respuesta = copilot.procesar_consulta_con_evidencia(
            consulta_original,
            chunks_evidencia,
            {
                "sintomas": [
                    s.sintoma for s in analisis_completo.consulta_procesada.sintomas
                ]
            },
        )

        print(f"   ✅ Análisis clínico completado")
        print(
            f"   📋 Recomendación: {respuesta.respuesta_estructurada.recomendacion[:150]}..."
        )
        print(
            f"   🚨 Nivel urgencia: {respuesta.respuesta_estructurada.nivel_urgencia.value}"
        )

        print("\n✅ Prueba del caso de rodilla completada!")
        return True

    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_caso_rodilla()
    sys.exit(0 if success else 1)
