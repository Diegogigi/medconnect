#!/usr/bin/env python3
"""
Script para probar la corrección del error de EvidenciaCientifica
"""

import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_correccion_evidencia():
    """Prueba la corrección del error de EvidenciaCientifica"""

    print("🧪 Probando corrección del error de EvidenciaCientifica...")
    print("=" * 60)

    try:
        # 1. Crear evidencia científica de prueba
        print("1️⃣ Creando evidencia científica de prueba...")
        from unified_scientific_search_enhanced import EvidenciaCientifica

        evidencia_cientifica = [
            EvidenciaCientifica(
                titulo="Knee Pain Treatment: A Systematic Review",
                autores=["Smith J", "Johnson A", "Brown M"],
                doi="10.1234/test.2024.001",
                fecha_publicacion="2024-01-15",
                resumen="This systematic review examines the effectiveness of physical therapy interventions for knee pain management. Results show significant improvements in pain reduction and functional outcomes.",
                nivel_evidencia="Nivel I",
                fuente="pubmed",
                url="https://doi.org/10.1234/test.2024.001",
                relevancia_score=0.85,
                año_publicacion="2024",
                tipo_evidencia="Systematic Review",
            )
        ]

        print(f"   ✅ Creadas {len(evidencia_cientifica)} evidencias científicas")

        # 2. Convertir a ChunkEvidencia
        print("\n2️⃣ Convirtiendo a ChunkEvidencia...")
        from unified_copilot_assistant_enhanced import ChunkEvidencia

        chunks_evidencia = []
        for ev in evidencia_cientifica:
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

        print(f"   ✅ Convertidas {len(chunks_evidencia)} evidencias a chunks")

        # 3. Probar análisis clínico
        print("\n3️⃣ Probando análisis clínico...")
        from unified_copilot_assistant_enhanced import UnifiedCopilotAssistantEnhanced

        copilot = UnifiedCopilotAssistantEnhanced()

        consulta = "dolor de rodilla por golpe en el trabajo"
        contexto = {"sintomas": ["dolor de rodilla"]}

        respuesta = copilot.procesar_consulta_con_evidencia(
            consulta, chunks_evidencia, contexto
        )

        print(f"   ✅ Análisis clínico completado")
        print(
            f"   📋 Recomendación: {respuesta.respuesta_estructurada.recomendacion[:100]}..."
        )

        print("\n✅ Prueba de corrección completada exitosamente!")
        return True

    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_correccion_evidencia()
    sys.exit(0 if success else 1)
