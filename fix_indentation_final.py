#!/usr/bin/env python3
"""
Script para corregir el error de indentación final
"""


def fix_indentation_final():
    """Corrige el error de indentación final"""

    app_py_path = "app.py"

    print("🔧 Corrigiendo error de indentación final...")

    # Leer el archivo
    with open(app_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y corregir el error específico
    lines = content.split("\n")
    corrected_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Corregir línea problemática
        if 'logger.error(f"[ERROR] Error importando SheetsManager: {e}")' in line:
            # Verificar indentación
            if not line.startswith("        "):
                line = "        " + line.lstrip()
                print("✅ Corregida indentación de línea de error")

        corrected_lines.append(line)
        i += 1

    # Unir las líneas corregidas
    corrected_content = "\n".join(corrected_lines)

    # Escribir el archivo corregido
    with open(app_py_path, "w", encoding="utf-8") as f:
        f.write(corrected_content)

    print("✅ Error de indentación corregido")
    return True


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
    print("🔧 Corrigiendo error de indentación final...")

    if fix_indentation_final():
        print("✅ Error de indentación corregido")

        if verify_syntax():
            print("✅ Sintaxis verificada")

            if test_server():
                print("✅ Servidor puede iniciarse")
                print("\n🎉 ¡Error de indentación solucionado!")
                print("🚀 Ahora puedes ejecutar: python app.py")
            else:
                print("❌ Error en servidor")
        else:
            print("❌ Error de sintaxis")
    else:
        print("❌ No se pudo corregir el error de indentación")


if __name__ == "__main__":
    main()
