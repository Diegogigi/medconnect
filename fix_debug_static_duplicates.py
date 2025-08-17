#!/usr/bin/env python3
"""
Script para eliminar los endpoints debug_static duplicados
"""


def fix_debug_static_duplicates():
    """Elimina los endpoints debug_static duplicados"""

    app_py_path = "app.py"

    print("🔧 Eliminando endpoints debug_static duplicados...")

    # Leer el archivo
    with open(app_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y eliminar endpoints duplicados
    lines = content.split("\n")
    corrected_lines = []

    # Contador para debug_static
    debug_static_count = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detectar endpoint debug_static
        if "@app.route('/debug-static')" in line:
            debug_static_count += 1
            if debug_static_count > 1:
                print(
                    f"✅ Eliminando endpoint debug_static duplicado #{debug_static_count}"
                )
                # Saltar hasta el final de la función
                while i < len(lines) and not lines[i].strip().startswith("def "):
                    i += 1
                continue

        corrected_lines.append(line)
        i += 1

    # Unir las líneas corregidas
    corrected_content = "\n".join(corrected_lines)

    # Escribir el archivo corregido
    with open(app_py_path, "w", encoding="utf-8") as f:
        f.write(corrected_content)

    print("✅ Endpoints debug_static duplicados eliminados")
    return True


def verify_no_duplicates():
    """Verifica que no haya endpoints duplicados"""

    print("🔍 Verificando que no haya endpoints duplicados...")

    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Contar debug_static
        debug_static_count = content.count("@app.route('/debug-static')")

        if debug_static_count <= 1:
            print("✅ No hay endpoints debug_static duplicados")
            return True
        else:
            print(f"❌ Hay {debug_static_count} endpoints debug_static")
            return False

    except Exception as e:
        print(f"❌ Error verificando endpoints: {e}")
        return False


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
    print("🔧 Eliminando endpoints debug_static duplicados...")

    if fix_debug_static_duplicates():
        print("✅ Endpoints duplicados eliminados")

        if verify_no_duplicates():
            print("✅ Verificación de duplicados exitosa")

            if verify_syntax():
                print("✅ Sintaxis verificada")

                if test_server():
                    print("✅ Servidor puede iniciarse")
                    print("\n🎉 ¡Endpoints duplicados eliminados!")
                    print("🚀 Ahora puedes ejecutar: python app.py")
                else:
                    print("❌ Error en servidor")
            else:
                print("❌ Error de sintaxis")
        else:
            print("❌ Aún hay endpoints duplicados")
    else:
        print("❌ No se pudieron eliminar los endpoints")


if __name__ == "__main__":
    main()
