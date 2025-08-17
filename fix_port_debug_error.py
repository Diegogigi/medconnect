#!/usr/bin/env python3
"""
Script para corregir el error de variables port y debug no definidas
"""


def fix_port_debug_error():
    """Corrige el error de variables port y debug no definidas"""

    app_py_path = "app.py"

    print("🔧 Corrigiendo error de variables port y debug...")

    # Leer el archivo
    with open(app_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y corregir el problema
    old_line = '    app.run(host="0.0.0.0", port=port, debug=debug)'
    new_lines = """    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)"""

    if old_line in content:
        content = content.replace(old_line, new_lines)
        print("✅ Variables port y debug definidas correctamente")
    else:
        print("⚠️ No se encontró la línea problemática")
        return False

    # Verificar que os esté importado
    if "import os" not in content:
        # Buscar donde agregar el import
        import_section = content.find("import logging")
        if import_section != -1:
            content = (
                content[:import_section] + "import os\n" + content[import_section:]
            )
            print("✅ Import de os agregado")

    # Escribir el archivo corregido
    with open(app_py_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Archivo corregido")
    return True


def verify_fix():
    """Verifica que el error esté corregido"""

    app_py_path = "app.py"

    try:
        # Intentar importar el archivo para verificar sintaxis
        import ast

        with open(app_py_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Verificar sintaxis
        ast.parse(content)
        print("✅ Sintaxis del archivo verificada correctamente")

        # Verificar que las variables estén definidas
        if 'port = int(os.environ.get("PORT", 5000))' in content:
            print("✅ Variable port definida correctamente")
        else:
            print("❌ Variable port no definida")
            return False

        if 'debug = os.environ.get("FLASK_ENV") == "development"' in content:
            print("✅ Variable debug definida correctamente")
        else:
            print("❌ Variable debug no definida")
            return False

        return True

    except SyntaxError as e:
        print(f"❌ Error de sintaxis: {e}")
        return False
    except Exception as e:
        print(f"❌ Error verificando archivo: {e}")
        return False


def test_server_start():
    """Prueba que el servidor pueda iniciarse"""

    print("🧪 Probando inicio del servidor...")

    try:
        # Importar el módulo
        import importlib.util

        spec = importlib.util.spec_from_file_location("app", "app.py")
        module = importlib.util.module_from_spec(spec)

        # Verificar que las variables estén disponibles
        if hasattr(module, "app"):
            print("✅ Aplicación Flask disponible")
        else:
            print("❌ Aplicación Flask no disponible")
            return False

        print("✅ Servidor puede iniciarse correctamente")
        return True

    except Exception as e:
        print(f"❌ Error probando servidor: {e}")
        return False


def main():
    """Función principal"""
    print("🔧 Corrigiendo error de variables port y debug...")

    if fix_port_debug_error():
        print("✅ Error corregido")

        if verify_fix():
            print("✅ Verificación exitosa")

            if test_server_start():
                print("✅ Servidor puede iniciarse")
                print("\n🎉 ¡Error solucionado!")
                print("🚀 Ahora puedes ejecutar: python app.py")
            else:
                print("❌ Error en inicio del servidor")
        else:
            print("❌ Verificación falló")
    else:
        print("❌ No se pudo corregir el error")


if __name__ == "__main__":
    main()
