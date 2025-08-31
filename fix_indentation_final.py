#!/usr/bin/env python3
"""
Script para corregir los problemas de indentación finales
"""


def fix_indentation_final():
    """Corrige los problemas de indentación finales"""

    print("🔧 Corrigiendo problemas de indentación finales...")

    # Leer el archivo
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Corregir líneas con indentación incorrecta
    fixes = [
        (
            '        logger.error(f"Error: {e}")',
            '            logger.error(f"Error: {e}")',
        ),
        (
            '        return jsonify({"error": "Error interno del servidor"}), 500',
            '            return jsonify({"error": "Error interno del servidor"}), 500',
        ),
        (
            '        logger.error(f"Error: {e}")',
            '            logger.error(f"Error: {e}")',
        ),
        (
            '        return jsonify({"error": "Error interno del servidor"}), 500',
            '            return jsonify({"error": "Error interno del servidor"}), 500',
        ),
    ]

    for old, new in fixes:
        content = content.replace(old, new)

    # Escribir el archivo corregido
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Problemas de indentación finales corregidos")


if __name__ == "__main__":
    fix_indentation_final()
