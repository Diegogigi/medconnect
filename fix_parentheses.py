#!/usr/bin/env python3
"""
Script para corregir los errores de paréntesis en app.py
"""


def fix_parentheses():
    """Corrige los errores de paréntesis"""

    print("🔧 Corrigiendo errores de paréntesis...")

    # Leer el archivo
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Corregir paréntesis comentados problemáticos
    fixes = [
        # Línea 2041
        ("#             ),", "            ),"),
        # Línea 2070
        ("#     #             ),", "                ),"),
        # Línea 2075
        ("#             )", "            )"),
        # Línea 2085
        ("#             )", "            )"),
    ]

    for old, new in fixes:
        content = content.replace(old, new)

    # Escribir el archivo corregido
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Errores de paréntesis corregidos")


if __name__ == "__main__":
    fix_parentheses()
