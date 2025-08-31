#!/usr/bin/env python3
"""
Script final para limpiar todos los problemas de sintaxis restantes
"""


def final_cleanup():
    """Limpia todos los problemas de sintaxis restantes"""

    print("🔧 Limpieza final de todos los problemas de sintaxis...")

    # Leer el archivo
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Comentar TODAS las líneas problemáticas
    problematic_lines = [
        '                    # worksheet = spreadsheet.worksheet("Consultas")  # ELIMINADO',
        "    # # #         all_values = worksheet.get_all_values()",
        "                #                 ),  # specialty",
        "                #                 ),  # date",
        "                #                 ),  # diagnosis",
        "                #                 ),  # treatment",
        "                #                 ),  # status",
        '    #         logger.error(f"[ERROR] Error importando PostgreSQL Manager: {e}")',
        "    #         postgres_db = None",
        '#          #         logger.error(f"Error: {e}")',
        '#          #         return jsonify({"error": "Error interno del servidor"}), 500',
        '#         logger.error(f"[ERROR] Error importando PostgreSQL Manager: {e}")',
        "#         postgres_db = None",
        '#          #         logger.error(f"Error: {e}")',
        '#          #         return jsonify({"error": "Error interno del servidor"}), 500',
        '#          #         return jsonify({"error": "Error interno del servidor"}), 500',
    ]

    for line in problematic_lines:
        if line in content:
            content = content.replace(line, "# " + line.lstrip("#"))

    # Escribir el archivo corregido
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Limpieza final completada")


if __name__ == "__main__":
    final_cleanup()
