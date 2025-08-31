#!/usr/bin/env python3
"""
Script para corregir específicamente el paréntesis comentado en la línea 1036
"""


def fix_specific_parentheses():
    """Corrige específicamente el paréntesis comentado"""

    print("🔧 Corrigiendo paréntesis específico...")

    # Leer el archivo
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Corregir el paréntesis específico
    content = content.replace(
        "        #                  ),  # Obtenido de la hoja de usuarios",
        "                        ),  # Obtenido de la hoja de usuarios",
    )

    # Escribir el archivo corregido
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Paréntesis específico corregido")


if __name__ == "__main__":
    fix_specific_parentheses()
