#!/usr/bin/env python3
"""
Script para cambiar la imagen del register a robot_e-health.png
"""


def change_register_to_robot():
    """Cambia la imagen del register a robot_e-health.png"""

    print("🤖 Cambiando imagen del register a robot_e-health.png...")

    # Leer el archivo actual
    with open("templates/register.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Cambiar logo.png por robot_e-health.png
    content = content.replace(
        "src=\"{{ url_for('static', filename='images/logo.png') }}\"",
        "src=\"{{ url_for('static', filename='images/robot_e-health.png') }}\"",
    )

    # Cambiar el alt text también
    content = content.replace('alt="MedConnect Logo"', 'alt="Robot E-Health"')

    # Escribir el archivo actualizado
    with open("templates/register.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Imagen del register cambiada:")
    print("   - Panel izquierdo: robot_e-health.png")
    print("   - Alt text actualizado")
    print("   - Tamaño mantenido (250px x 250px)")


if __name__ == "__main__":
    change_register_to_robot()
