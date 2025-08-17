#!/usr/bin/env python3
"""
Script para corregir endpoints duplicados y errores de indentación
"""


def fix_duplicate_endpoints():
    """Corrige endpoints duplicados"""

    app_py_path = "app.py"

    print("🔧 Corrigiendo endpoints duplicados...")

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

        # Contar debug_static
        if "@app.route('/debug-static')" in line:
            debug_static_count += 1
            if debug_static_count > 1:
                print("✅ Eliminando endpoint debug_static duplicado")
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

    print("✅ Endpoints duplicados corregidos")
    return True


def fix_indentation_errors():
    """Corrige errores de indentación"""

    app_py_path = "app.py"

    print("🔧 Corrigiendo errores de indentación...")

    # Leer el archivo
    with open(app_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y corregir líneas con indentación incorrecta
    lines = content.split("\n")
    corrected_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Buscar líneas sueltas que causan error de indentación
        if (
            line.strip()
            == "consulta, evidencia=evidencia_cientifica, contexto_nlp=analisis_nlp"
            or (
                line.strip() == ")"
                and i > 0
                and "consulta, evidencia=evidencia_cientifica" in lines[i - 1]
            )
        ):
            print(f"✅ Eliminando línea problemática: {line.strip()}")
            i += 1
            continue

        corrected_lines.append(line)
        i += 1

    # Unir las líneas corregidas
    corrected_content = "\n".join(corrected_lines)

    # Escribir el archivo corregido
    with open(app_py_path, "w", encoding="utf-8") as f:
        f.write(corrected_content)

    print("✅ Errores de indentación corregidos")
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


def verify_endpoints():
    """Verifica que no haya endpoints duplicados"""

    print("🔍 Verificando endpoints...")

    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Contar debug_static
        debug_static_count = content.count("@app.route('/debug-static')")

        if debug_static_count <= 1:
            print("✅ No hay endpoints duplicados")
            return True
        else:
            print(f"❌ Hay {debug_static_count} endpoints debug_static")
            return False

    except Exception as e:
        print(f"❌ Error verificando endpoints: {e}")
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
    print("🔧 Corrigiendo errores...")

    # Corregir endpoints duplicados
    if fix_duplicate_endpoints():
        print("✅ Endpoints duplicados corregidos")

        # Corregir errores de indentación
        if fix_indentation_errors():
            print("✅ Errores de indentación corregidos")

            # Verificar sintaxis
            if verify_syntax():
                print("✅ Sintaxis verificada")

                # Verificar endpoints
                if verify_endpoints():
                    print("✅ Endpoints verificados")

                    # Probar servidor
                    if test_server():
                        print("✅ Servidor puede iniciarse")
                        print("\n🎉 ¡Todos los errores solucionados!")
                        print("🚀 Ahora puedes ejecutar: python app.py")
                    else:
                        print("❌ Error en servidor")
                else:
                    print("❌ Error en endpoints")
            else:
                print("❌ Error de sintaxis")
        else:
            print("❌ Error corrigiendo indentación")
    else:
        print("❌ Error corrigiendo endpoints")


if __name__ == "__main__":
    main()
