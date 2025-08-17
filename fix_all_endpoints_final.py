#!/usr/bin/env python3
"""
Script para eliminar todos los endpoints duplicados de una vez
"""


def fix_all_endpoints_final():
    """Elimina todos los endpoints duplicados de una vez"""

    app_py_path = "app.py"

    print("🔧 Eliminando todos los endpoints duplicados...")

    # Leer el archivo
    with open(app_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y eliminar todos los endpoints duplicados
    lines = content.split("\n")
    corrected_lines = []

    # Contadores para endpoints
    endpoint_counts = {}

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detectar endpoints
        if "@app.route(" in line:
            # Extraer nombre del endpoint
            import re

            match = re.search(r'@app\.route\([\'"]([^\'"]+)[\'"]', line)
            if match:
                endpoint_name = match.group(1)

                # Contar endpoint
                if endpoint_name not in endpoint_counts:
                    endpoint_counts[endpoint_name] = 0
                endpoint_counts[endpoint_name] += 1

                # Si es duplicado, eliminar
                if endpoint_counts[endpoint_name] > 1:
                    print(f"✅ Eliminando endpoint duplicado: {endpoint_name}")
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

    print("✅ Todos los endpoints duplicados eliminados")

    # Mostrar resumen
    print("\n📊 Resumen de endpoints:")
    for endpoint, count in endpoint_counts.items():
        if count > 1:
            print(f"   ❌ {endpoint}: {count} veces (corregido)")
        else:
            print(f"   ✅ {endpoint}: {count} vez")

    return True


def verify_no_duplicates():
    """Verifica que no haya endpoints duplicados"""

    print("🔍 Verificando que no haya endpoints duplicados...")

    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Buscar todos los endpoints
        import re

        endpoints = re.findall(r'@app\.route\([\'"]([^\'"]+)[\'"]', content)

        # Contar duplicados
        from collections import Counter

        endpoint_counts = Counter(endpoints)

        duplicates = [
            endpoint for endpoint, count in endpoint_counts.items() if count > 1
        ]

        if not duplicates:
            print("✅ No hay endpoints duplicados")
            return True
        else:
            print(f"❌ Endpoints duplicados encontrados: {duplicates}")
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
    print("🔧 Eliminando todos los endpoints duplicados...")

    if fix_all_endpoints_final():
        print("✅ Endpoints duplicados eliminados")

        if verify_no_duplicates():
            print("✅ Verificación de duplicados exitosa")

            if verify_syntax():
                print("✅ Sintaxis verificada")

                if test_server():
                    print("✅ Servidor puede iniciarse")
                    print("\n🎉 ¡Todos los endpoints duplicados eliminados!")
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
