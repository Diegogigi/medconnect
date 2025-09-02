#!/usr/bin/env python3
"""
Script para corregir los colores del panel izquierdo
"""


def fix_panel_colors():
    """Corrige los colores del panel izquierdo"""

    print("🔧 Corrigiendo colores del panel izquierdo...")

    # Leer el archivo actual
    with open("templates/login.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Corregir el panel izquierdo para que tenga el gradiente correcto
    content = content.replace(
        "background: #f8fafc;",
        "background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);",
    )

    # Escribir el archivo corregido
    with open("templates/login.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Colores corregidos:")
    print("   - Panel izquierdo: gradiente #6366f1 a #8b5cf6")
    print("   - Fondo principal: blanco/gris claro")
    print("   - Panel derecho: blanco")


if __name__ == "__main__":
    fix_panel_colors()
