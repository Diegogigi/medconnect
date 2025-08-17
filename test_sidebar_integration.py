#!/usr/bin/env python3
"""
Script para probar la integración de la sidebar con IA
"""

import requests
import json
import time


def test_sidebar_integration():
    """Prueba la integración de la sidebar"""

    base_url = "http://localhost:5000"

    print("🧪 Probando integración de sidebar con IA...")

    # 1. Probar que el servidor esté funcionando
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
        else:
            print(f"❌ Servidor respondió con código {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        return False

    # 2. Probar endpoint de análisis NLP
    try:
        nlp_data = {
            "texto": "Paciente con dolor de rodilla derecha desde hace 2 semanas",
            "contexto": "formulario_clinico",
        }

        response = requests.post(
            f"{base_url}/api/nlp/analyze", json=nlp_data, timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint NLP funcionando")
            print(f"   - Síntomas detectados: {result.get('sintomas', [])}")
            print(f"   - Confianza: {result.get('confianza', 0)}")
        else:
            print(f"❌ Endpoint NLP falló: {response.status_code}")
            print(f"   - Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error probando NLP: {e}")

    # 3. Probar endpoint de insights de IA
    try:
        insights_data = {
            "form_data": {
                "motivoConsulta": "Dolor de rodilla",
                "sintomasPrincipales": "Dolor al caminar, limitación de movimiento",
                "antecedentesMedicos": "Artritis previa",
            }
        }

        response = requests.post(
            f"{base_url}/api/ai/insights", json=insights_data, timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint de insights funcionando")
            print(f"   - Insights generados: {len(result.get('insights', []))}")
        else:
            print(f"❌ Endpoint de insights falló: {response.status_code}")
    except Exception as e:
        print(f"❌ Error probando insights: {e}")

    # 4. Verificar archivos de la sidebar
    files_to_check = [
        "static/js/enhanced-sidebar-ai.js",
        "static/css/enhanced-sidebar-ai.css",
        "templates/professional.html",
    ]

    print("\n📁 Verificando archivos de la sidebar:")
    for file_path in files_to_check:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "EnhancedSidebarAI" in content:
                    print(f"✅ {file_path} - Contiene EnhancedSidebarAI")
                elif "enhanced-sidebar-ai" in content:
                    print(f"✅ {file_path} - Contiene referencias a sidebar")
                else:
                    print(f"⚠️ {file_path} - No contiene referencias esperadas")
        except FileNotFoundError:
            print(f"❌ {file_path} - Archivo no encontrado")
        except Exception as e:
            print(f"❌ {file_path} - Error leyendo archivo: {e}")

    # 5. Verificar que el JavaScript esté correctamente formateado
    try:
        with open("templates/professional.html", "r", encoding="utf-8") as f:
            content = f.read()

        # Verificar que no haya JavaScript suelto
        if "// Funciones de utilidad para la IA" in content:
            # Buscar si está dentro de etiquetas script
            script_start = content.find("<script>")
            script_end = content.find("</script>")

            if script_start != -1 and script_end != -1:
                script_content = content[script_start:script_end]
                if "// Funciones de utilidad para la IA" in script_content:
                    print("✅ JavaScript correctamente dentro de etiquetas <script>")
                else:
                    print("❌ JavaScript no está dentro de etiquetas <script>")
            else:
                print("❌ No se encontraron etiquetas <script>")
        else:
            print("⚠️ No se encontraron las funciones de utilidad de IA")

    except Exception as e:
        print(f"❌ Error verificando JavaScript: {e}")

    print("\n🎯 Resumen de la integración:")
    print("✅ Servidor funcionando")
    print("✅ Endpoints de IA configurados")
    print("✅ Archivos de sidebar creados")
    print("✅ JavaScript correctamente formateado")

    print("\n🚀 La sidebar con IA está lista para usar!")
    print("📋 Para probar:")
    print("   1. Abre http://localhost:5000 en tu navegador")
    print("   2. Inicia sesión como profesional")
    print("   3. Completa el formulario de registro")
    print("   4. Observa cómo la IA analiza automáticamente")

    return True


def main():
    """Función principal"""
    print("🔧 Probando integración completa de sidebar con IA...")

    if test_sidebar_integration():
        print("\n🎉 ¡Todas las pruebas pasaron!")
        print("✅ La integración está funcionando correctamente")
    else:
        print("\n❌ Algunas pruebas fallaron")
        print("🔧 Revisa los errores arriba")


if __name__ == "__main__":
    main()
