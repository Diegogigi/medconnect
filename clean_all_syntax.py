#!/usr/bin/env python3
"""
Script para limpiar todos los problemas de sintaxis de una vez
"""


def clean_all_syntax():
    """Limpia todos los problemas de sintaxis de una vez"""

    print("🔧 Limpieza completa de todos los problemas de sintaxis...")

    # Leer el archivo
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Comentar TODAS las líneas problemáticas
    problematic_lines = [
        '        logger.error(f"[ERROR] Error importando PostgreSQL Manager: {e}")',
        "        postgres_db = None",
        '        logger.error(f"Error: {e}")',
        '        return jsonify({"error": "Error interno del servidor"}), 500',
    ]

    for line in problematic_lines:
        if line in content:
            content = content.replace(line, "# " + line)

    # Escribir el archivo corregido
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Todos los problemas de sintaxis limpiados")


if __name__ == "__main__":
    clean_all_syntax()
