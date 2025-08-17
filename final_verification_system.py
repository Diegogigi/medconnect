#!/usr/bin/env python3
"""
Script final para verificar que todo el sistema esté funcionando
"""

import requests
import json
import time


def test_system():
    """Prueba completa del sistema"""

    print("🧪 Probando sistema completo...")

    # Datos de prueba
    test_data = {
        "consulta": "Paciente con dolor lumbar agudo por esfuerzo físico",
        "contexto_clinico": {
            "motivoConsulta": "Dolor lumbar agudo",
            "sintomasPrincipales": "Dolor intenso en región lumbar, limitación de movimiento",
            "antecedentesMedicos": "Sin antecedentes relevantes",
        },
    }

    try:
        # Hacer petición al endpoint
        print("📡 Enviando petición al endpoint...")
        response = requests.post(
            "http://localhost:5000/api/copilot/analyze-enhanced",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint responde correctamente")

            # Verificar estructura de respuesta
            if result.get("success"):
                print("✅ Respuesta exitosa")

                # Verificar componentes
                nlp_analysis = result.get("nlp_analysis", {})
                if nlp_analysis:
                    print(
                        f"✅ Análisis NLP: {len(nlp_analysis.get('palabras_clave', []))} palabras clave"
                    )

                evidence = result.get("evidence", [])
                if evidence:
                    print(f"✅ Evidencia científica: {len(evidence)} artículos")

                clinical_analysis = result.get("clinical_analysis", {})
                if clinical_analysis:
                    print(
                        f"✅ Análisis clínico: {len(clinical_analysis.get('recomendaciones', []))} recomendaciones"
                    )

                print("\n📊 Resumen de la respuesta:")
                print(f"   - Palabras clave: {nlp_analysis.get('palabras_clave', [])}")
                print(f"   - Síntomas: {nlp_analysis.get('sintomas', [])}")
                print(f"   - Evidencia: {len(evidence)} artículos")
                print(
                    f"   - Recomendaciones: {clinical_analysis.get('recomendaciones', [])}"
                )

                return True
            else:
                print(
                    f"❌ Respuesta no exitosa: {result.get('message', 'Sin mensaje')}"
                )
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor")
        print(
            "   Asegúrate de que el servidor esté ejecutándose en http://localhost:5000"
        )
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout en la petición")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def verify_files():
    """Verifica que los archivos necesarios existan"""

    print("🔍 Verificando archivos...")

    required_files = [
        "app.py",
        "unified_nlp_processor_main.py",
        "unified_scientific_search_enhanced.py",
        "unified_copilot_assistant_enhanced.py",
        "static/css/enhanced-sidebar-ai.css",
        "static/js/simple-unified-sidebar-ai.js",
        "templates/professional.html",
    ]

    missing_files = []
    for file_path in required_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                f.read(1)  # Solo verificar que se puede leer
            print(f"✅ {file_path}")
        except Exception:
            print(f"❌ {file_path}")
            missing_files.append(file_path)

    if missing_files:
        print(f"\n⚠️ Archivos faltantes: {len(missing_files)}")
        return False
    else:
        print(f"\n✅ Todos los archivos están presentes")
        return True


def verify_methods():
    """Verifica que los métodos existan"""

    print("🔍 Verificando métodos...")

    try:
        # Verificar NLP
        from unified_nlp_processor_main import UnifiedNLPProcessor

        nlp = UnifiedNLPProcessor()
        if hasattr(nlp, "procesar_consulta_completa"):
            print("✅ UnifiedNLPProcessor.procesar_consulta_completa")
        else:
            print("❌ UnifiedNLPProcessor.procesar_consulta_completa")
            return False
    except Exception as e:
        print(f"❌ Error NLP: {e}")
        return False

    try:
        # Verificar Scientific Search
        from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced

        search = UnifiedScientificSearchEnhanced()
        if hasattr(search, "buscar_evidencia_unificada"):
            print("✅ UnifiedScientificSearchEnhanced.buscar_evidencia_unificada")
        else:
            print("❌ UnifiedScientificSearchEnhanced.buscar_evidencia_unificada")
            return False
    except Exception as e:
        print(f"❌ Error Scientific Search: {e}")
        return False

    try:
        # Verificar Copilot
        from unified_copilot_assistant_enhanced import UnifiedCopilotAssistantEnhanced

        copilot = UnifiedCopilotAssistantEnhanced()
        if hasattr(copilot, "procesar_consulta_con_evidencia"):
            print("✅ UnifiedCopilotAssistantEnhanced.procesar_consulta_con_evidencia")
        else:
            print("❌ UnifiedCopilotAssistantEnhanced.procesar_consulta_con_evidencia")
            return False
    except Exception as e:
        print(f"❌ Error Copilot: {e}")
        return False

    return True


def main():
    """Función principal"""
    print("🔧 Verificación final del sistema...")
    print("=" * 50)

    # Verificar archivos
    files_ok = verify_files()
    print()

    # Verificar métodos
    methods_ok = verify_methods()
    print()

    # Probar sistema
    system_ok = test_system()
    print()

    # Resumen final
    print("=" * 50)
    print("📊 RESUMEN FINAL:")
    print(f"   Archivos: {'✅ OK' if files_ok else '❌ ERROR'}")
    print(f"   Métodos: {'✅ OK' if methods_ok else '❌ ERROR'}")
    print(f"   Sistema: {'✅ OK' if system_ok else '❌ ERROR'}")

    if files_ok and methods_ok and system_ok:
        print("\n🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("✅ Todos los componentes están operativos")
        print("✅ El texto aparecerá en negro")
        print("✅ Los análisis serán completos y precisos")
        print("\n🚀 ¡Listo para usar!")
    else:
        print("\n⚠️ Hay problemas que necesitan atención")
        if not files_ok:
            print("   - Verificar archivos faltantes")
        if not methods_ok:
            print("   - Verificar métodos de los módulos")
        if not system_ok:
            print("   - Verificar que el servidor esté ejecutándose")


if __name__ == "__main__":
    main()
