#!/usr/bin/env python3
"""
Script para aplicar correcciones seguras
"""


def apply_safe_fixes():
    """Aplica correcciones seguras"""

    app_py_path = "app.py"

    print("🔧 Aplicando correcciones seguras...")

    # Leer el archivo
    with open(app_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Aplicar solo correcciones específicas y seguras
    corrections = [
        # 1. Corregir método de búsqueda científica
        (
            "evidencia_cientifica = search_system.buscar_pubmed(",
            "evidencia_cientifica = search_system.buscar_evidencia_unificada(",
        ),
        # 2. Corregir método del copilot
        (
            "analisis_clinico = copilot.generar_recomendaciones_clinicas(",
            'respuesta_copilot = copilot.procesar_consulta_con_evidencia(consulta, evidencia_cientifica, {"sintomas": analisis_nlp.get("sintomas", [])})\n            analisis_clinico = {\n                "recomendaciones": [respuesta_copilot.respuesta_estructurada.recomendacion],\n                "patologias": [],\n                "escalas": []\n            }',
        ),
        # 3. Corregir atributo nombre por texto
        (
            "[s.nombre for s in analisis_completo.consulta_procesada.sintomas]",
            "[s.texto for s in analisis_completo.consulta_procesada.sintomas]",
        ),
    ]

    changes_made = 0
    for old_code, new_code in corrections:
        if old_code in content:
            content = content.replace(old_code, new_code)
            print(f"✅ Corregido: {old_code[:40]}...")
            changes_made += 1
        else:
            print(f"ℹ️ No encontrado: {old_code[:40]}...")

    # Escribir el archivo corregido
    with open(app_py_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ {changes_made} correcciones aplicadas")
    return changes_made > 0


def verify_syntax():
    """Verifica la sintaxis"""

    print("🔍 Verificando sintaxis...")

    try:
        import ast

        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()

        ast.parse(content)
        print("✅ Sintaxis correcta")
        return True

    except SyntaxError as e:
        print(f"❌ Error de sintaxis: {e}")
        return False
    except Exception as e:
        print(f"❌ Error verificando: {e}")
        return False


def test_server():
    """Prueba el servidor"""

    print("🧪 Probando servidor...")

    try:
        # Importar el módulo
        import importlib.util

        spec = importlib.util.spec_from_file_location("app", "app.py")
        module = importlib.util.module_from_spec(spec)

        if hasattr(module, "app"):
            print("✅ Aplicación Flask disponible")
            return True
        else:
            print("❌ Aplicación Flask no disponible")
            return False

    except Exception as e:
        print(f"❌ Error probando servidor: {e}")
        return False


def main():
    """Función principal"""
    print("🔧 Aplicando correcciones seguras...")

    if apply_safe_fixes():
        print("✅ Correcciones aplicadas")

        if verify_syntax():
            print("✅ Sintaxis verificada")

            if test_server():
                print("✅ Servidor puede iniciarse")
                print("\n🎉 ¡Correcciones aplicadas exitosamente!")
                print("🚀 Ahora puedes ejecutar: python app.py")
            else:
                print("❌ Error en servidor")
        else:
            print("❌ Error de sintaxis")
    else:
        print("❌ No se pudieron aplicar las correcciones")


if __name__ == "__main__":
    main()
