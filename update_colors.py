#!/usr/bin/env python3
"""
Script para actualizar los colores del fondo y paneles
"""


def update_colors():
    """Actualiza los colores del fondo y paneles"""

    print("🎨 Actualizando colores del diseño...")

    # Leer el archivo actual
    with open("templates/login.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Cambiar el fondo principal a blanco/gris muy claro
    content = content.replace("background: var(--gradient-bg);", "background: #f8fafc;")

    # 2. Cambiar el panel izquierdo a #6366f1 con gradiente a #8b5cf6
    content = content.replace(
        "background: var(--gradient-bg);",
        "background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);",
    )

    # Escribir el archivo actualizado
    with open("templates/login.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Colores actualizados:")
    print("   - Fondo principal: blanco/gris muy claro (#f8fafc)")
    print("   - Panel izquierdo: #6366f1 a #8b5cf6")
    print("   - Panel derecho: blanco (sin cambios)")


if __name__ == "__main__":
    update_colors()
