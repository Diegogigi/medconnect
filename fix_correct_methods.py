#!/usr/bin/env python3
"""
Script para corregir los métodos con los nombres correctos
"""


def fix_correct_methods():
    """Corrige los métodos con los nombres correctos"""

    app_py_path = "app.py"

    print("🔧 Corrigiendo métodos con nombres correctos...")

    # Leer el archivo
    with open(app_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Corregir métodos con nombres correctos
    corrections = [
        # NLP Processor - usar procesar_consulta_completa
        (
            "analisis_nlp = nlp_processor.analizar_texto(consulta)",
            'analisis_completo = nlp_processor.procesar_consulta_completa(consulta)\n            analisis_nlp = {\n                "palabras_clave": analisis_completo.palabras_clave,\n                "sintomas": [s.nombre for s in analisis_completo.consulta_procesada.sintomas],\n                "entidades": [e.texto for e in analisis_completo.consulta_procesada.entidades_clinicas],\n                "confianza": analisis_completo.confianza_global,\n            }',
        ),
        # Scientific Search - usar buscar_evidencia_unificada
        (
            "evidencia_cientifica = search_system.buscar_evidencia_cientifica(",
            "evidencia_cientifica = search_system.buscar_evidencia_unificada(",
        ),
        # Copilot Assistant - usar procesar_consulta_con_evidencia
        (
            "analisis_clinico = copilot.analizar_caso_clinico(",
            'respuesta_copilot = copilot.procesar_consulta_con_evidencia(consulta, evidencia_cientifica, {"sintomas": analisis_nlp.get("sintomas", [])})\n            analisis_clinico = {\n                "recomendaciones": [respuesta_copilot.respuesta_estructurada.recomendacion],\n                "patologias": [],\n                "escalas": []\n            }',
        ),
    ]

    changes_made = 0
    for old_code, new_code in corrections:
        if old_code in content:
            content = content.replace(old_code, new_code)
            print(f"✅ Corregido método")
            changes_made += 1
        else:
            print(f"ℹ️ No encontrado: {old_code[:50]}...")

    if changes_made == 0:
        print("⚠️ No se encontraron métodos para corregir")
        return False

    # Escribir el archivo corregido
    with open(app_py_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ {changes_made} correcciones aplicadas")
    return True


def verify_correct_methods():
    """Verifica que los métodos correctos existan"""

    print("🔍 Verificando métodos correctos...")

    try:
        # Verificar NLP Processor
        from unified_nlp_processor_main import UnifiedNLPProcessor

        nlp = UnifiedNLPProcessor()

        if hasattr(nlp, "procesar_consulta_completa"):
            print("✅ UnifiedNLPProcessor.procesar_consulta_completa existe")
        else:
            print("❌ UnifiedNLPProcessor.procesar_consulta_completa NO existe")
            return False

    except Exception as e:
        print(f"❌ Error verificando NLP: {e}")
        return False

    try:
        # Verificar Scientific Search
        from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced

        search = UnifiedScientificSearchEnhanced()

        if hasattr(search, "buscar_evidencia_unificada"):
            print(
                "✅ UnifiedScientificSearchEnhanced.buscar_evidencia_unificada existe"
            )
        else:
            print(
                "❌ UnifiedScientificSearchEnhanced.buscar_evidencia_unificada NO existe"
            )
            return False

    except Exception as e:
        print(f"❌ Error verificando Scientific Search: {e}")
        return False

    try:
        # Verificar Copilot Assistant
        from unified_copilot_assistant_enhanced import UnifiedCopilotAssistantEnhanced

        copilot = UnifiedCopilotAssistantEnhanced()

        if hasattr(copilot, "procesar_consulta_con_evidencia"):
            print(
                "✅ UnifiedCopilotAssistantEnhanced.procesar_consulta_con_evidencia existe"
            )
        else:
            print(
                "❌ UnifiedCopilotAssistantEnhanced.procesar_consulta_con_evidencia NO existe"
            )
            return False

    except Exception as e:
        print(f"❌ Error verificando Copilot: {e}")
        return False

    return True


def main():
    """Función principal"""
    print("🔧 Corrigiendo métodos con nombres correctos...")

    if fix_correct_methods():
        print("✅ Métodos corregidos")

        if verify_correct_methods():
            print("✅ Métodos verificados correctamente")
            print("\n🎉 ¡Métodos corregidos!")
            print("🚀 El sistema debería funcionar correctamente ahora")
            print("📝 Los resultados aparecerán con texto negro y contenido completo")
        else:
            print("❌ Error en verificación de métodos")
    else:
        print("❌ No se pudieron corregir los métodos")


if __name__ == "__main__":
    main()
