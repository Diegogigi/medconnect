#!/usr/bin/env python3
"""
Script para corregir los nombres de métodos incorrectos en app.py
"""


def fix_method_names():
    """Corrige los nombres de métodos incorrectos"""

    app_py_path = "app.py"

    print("🔧 Corrigiendo nombres de métodos...")

    # Leer el archivo
    with open(app_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Corregir nombres de métodos
    corrections = [
        # NLP Processor
        ("analizar__texto", "analizar_texto"),
        # Scientific Search
        ("buscaar_evidencia_cientifica", "buscar_evidencia_cientifica"),
        # Copilot Assistant
        ("analizarr_caso_clinico", "analizar_caso_clinico"),
    ]

    changes_made = 0
    for old_name, new_name in corrections:
        if old_name in content:
            content = content.replace(old_name, new_name)
            print(f"✅ Corregido: {old_name} → {new_name}")
            changes_made += 1
        else:
            print(f"ℹ️ No encontrado: {old_name}")

    if changes_made == 0:
        print("⚠️ No se encontraron métodos para corregir")
        return False

    # Escribir el archivo corregido
    with open(app_py_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ {changes_made} correcciones aplicadas")
    return True


def verify_methods():
    """Verifica que los métodos existan en los módulos"""

    print("🔍 Verificando métodos en módulos...")

    try:
        # Verificar NLP Processor
        from unified_nlp_processor_main import UnifiedNLPProcessor

        nlp = UnifiedNLPProcessor()

        if hasattr(nlp, "analizar_texto"):
            print("✅ UnifiedNLPProcessor.analizar_texto existe")
        else:
            print("❌ UnifiedNLPProcessor.analizar_texto NO existe")
            return False

    except Exception as e:
        print(f"❌ Error verificando NLP: {e}")
        return False

    try:
        # Verificar Scientific Search
        from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced

        search = UnifiedScientificSearchEnhanced()

        if hasattr(search, "buscar_evidencia_cientifica"):
            print(
                "✅ UnifiedScientificSearchEnhanced.buscar_evidencia_cientifica existe"
            )
        else:
            print(
                "❌ UnifiedScientificSearchEnhanced.buscar_evidencia_cientifica NO existe"
            )
            return False

    except Exception as e:
        print(f"❌ Error verificando Scientific Search: {e}")
        return False

    try:
        # Verificar Copilot Assistant
        from unified_copilot_assistant_enhanced import UnifiedCopilotAssistantEnhanced

        copilot = UnifiedCopilotAssistantEnhanced()

        if hasattr(copilot, "analizar_caso_clinico"):
            print("✅ UnifiedCopilotAssistantEnhanced.analizar_caso_clinico existe")
        else:
            print("❌ UnifiedCopilotAssistantEnhanced.analizar_caso_clinico NO existe")
            return False

    except Exception as e:
        print(f"❌ Error verificando Copilot: {e}")
        return False

    return True


def test_endpoint():
    """Prueba el endpoint con datos de ejemplo"""

    print("🧪 Probando endpoint...")

    try:
        import requests
        import json

        # Datos de prueba
        test_data = {
            "consulta": "Paciente con dolor lumbar agudo",
            "contexto_clinico": {
                "motivoConsulta": "Dolor lumbar",
                "sintomasPrincipales": "Dolor intenso en región lumbar",
                "antecedentesMedicos": "Sin antecedentes relevantes",
            },
        }

        # Hacer petición
        response = requests.post(
            "http://localhost:5000/api/copilot/analyze-enhanced",
            json=test_data,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint responde correctamente")
            print(f"📊 Resultado: {result.get('success', False)}")
            return True
        else:
            print(f"❌ Endpoint error: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error probando endpoint: {e}")
        return False


def main():
    """Función principal"""
    print("🔧 Corrigiendo errores de métodos...")

    if fix_method_names():
        print("✅ Nombres de métodos corregidos")

        if verify_methods():
            print("✅ Métodos verificados correctamente")

            print("\n🎉 ¡Errores solucionados!")
            print("🚀 El sistema debería funcionar correctamente ahora")
            print("📝 Los resultados aparecerán con texto negro y contenido completo")
        else:
            print("❌ Error en verificación de métodos")
    else:
        print("❌ No se pudieron corregir los métodos")


if __name__ == "__main__":
    main()
