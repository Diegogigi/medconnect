#!/usr/bin/env python3
"""
Script para corregir la imagen y color del panel izquierdo del register
"""


def fix_register_image_and_color():
    """Corrige la imagen y color del panel izquierdo del register"""

    print("🔧 Corrigiendo imagen y color del register...")

    # Leer el archivo actual
    with open("templates/register.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Cambiar la imagen a robot_e-health.png
    content = content.replace(
        "src=\"{{ url_for('static', filename='images/robot_e-health.png') }}\"",
        "src=\"{{ url_for('static', filename='images/robot_e-health.png') }}\"",
    )

    # 2. Cambiar el color del panel izquierdo a #6366f1
    content = content.replace("background: white;", "background: #6366f1;")

    # 3. Cambiar el color del texto del panel izquierdo a blanco
    content = content.replace("color: #1e293b;", "color: white;")

    # Escribir el archivo corregido
    with open("templates/register.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Register corregido:")
    print("   - Imagen: robot_e-health.png")
    print("   - Panel izquierdo: color #6366f1")
    print("   - Texto: blanco para contraste")


if __name__ == "__main__":
    fix_register_image_and_color()
