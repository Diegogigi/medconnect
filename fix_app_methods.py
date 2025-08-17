#!/usr/bin/env python3
"""
Script para corregir los nombres de métodos en app.py
"""


def fix_app_methods():
    """Corrige los nombres de métodos en app.py"""

    app_py_path = "app.py"

    print("🔧 Corrigiendo métodos en app.py...")

    # Leer el archivo
    with open(app_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Corregir métodos
    corrections = [
        # NLP Processor - cambiar analizar_texto por procesar_consulta_completa
        (
            "analisis_nlp = nlp_processor.analizar_texto(consulta)",
            'analisis_completo = nlp_processor.procesar_consulta_completa(consulta)\n            analisis_nlp = {\n                "palabras_clave": analisis_completo.palabras_clave,\n                "sintomas": [s.nombre for s in analisis_completo.consulta_procesada.sintomas],\n                "entidades": [e.texto for e in analisis_completo.consulta_procesada.entidades_clinicas],\n                "confianza": analisis_completo.confianza_global,\n            }',
        ),
        # Scientific Search - verificar método correcto
        (
            "evidencia_cientifica = search_system.buscar_evidencia_cientifica(",
            "evidencia_cientifica = search_system.buscar_pubmed(",
        ),
        # Copilot Assistant - verificar método correcto
        (
            "analisis_clinico = copilot.analizar_caso_clinico(",
            "analisis_clinico = copilot.generar_recomendaciones_clinicas(",
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


def verify_methods_exist():
    """Verifica que los métodos existan en los módulos"""

    print("🔍 Verificando métodos en módulos...")

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

        if hasattr(search, "buscar_pubmed"):
            print("✅ UnifiedScientificSearchEnhanced.buscar_pubmed existe")
        else:
            print("❌ UnifiedScientificSearchEnhanced.buscar_pubmed NO existe")
            return False

    except Exception as e:
        print(f"❌ Error verificando Scientific Search: {e}")
        return False

    try:
        # Verificar Copilot Assistant
        from unified_copilot_assistant_enhanced import UnifiedCopilotAssistantEnhanced

        copilot = UnifiedCopilotAssistantEnhanced()

        if hasattr(copilot, "generar_recomendaciones_clinicas"):
            print(
                "✅ UnifiedCopilotAssistantEnhanced.generar_recomendaciones_clinicas existe"
            )
        else:
            print(
                "❌ UnifiedCopilotAssistantEnhanced.generar_recomendaciones_clinicas NO existe"
            )
            return False

    except Exception as e:
        print(f"❌ Error verificando Copilot: {e}")
        return False

    return True


def main():
    """Función principal"""
    print("🔧 Corrigiendo métodos en app.py...")

    if fix_app_methods():
        print("✅ Métodos corregidos")

        if verify_methods_exist():
            print("✅ Métodos verificados correctamente")
            print("\n🎉 ¡Métodos corregidos!")
            print("🚀 El sistema debería funcionar correctamente ahora")
        else:
            print("❌ Error en verificación de métodos")
    else:
        print("❌ No se pudieron corregir los métodos")


if __name__ == "__main__":
    main()
