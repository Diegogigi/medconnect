#!/usr/bin/env python3
"""
Script para arreglar el error de sintaxis en app.py
"""


def fix_syntax_error():
    """Arregla el error de sintaxis en app.py"""

    print("🔧 Arreglando error de sintaxis en app.py...")

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar la línea problemática
    old_line = 'PORT = int(os.environ.get("PORT", "5000"))app = Flask(__name__)'
    new_lines = """PORT = int(os.environ.get("PORT", "5000"))

app = Flask(__name__)"""

    if old_line in content:
        content = content.replace(old_line, new_lines)

        # Escribir el archivo corregido
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Error de sintaxis corregido")
        print("🔧 Ahora la aplicación debería iniciar correctamente")
    else:
        print("❌ No se encontró la línea problemática")
        print("🔍 Verificando si hay otros errores de sintaxis...")

        # Verificar si hay otros problemas similares
        if "))app" in content:
            print("⚠️ Se encontraron otros posibles errores de sintaxis")
            print("   Buscando líneas pegadas...")

            # Buscar líneas que terminen en )) y empiecen con app
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "))app" in line:
                    print(f"   Línea {i+1}: {line[:50]}...")
        else:
            print("✅ No se encontraron otros errores de sintaxis")


if __name__ == "__main__":
    fix_syntax_error()
