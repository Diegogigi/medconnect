#!/usr/bin/env python3
"""
Script simple para cambiar el color del panel izquierdo
"""


def simple_color_fix():
    """Cambia el color del panel izquierdo a #6366f1"""

    print("🎨 Cambiando panel izquierdo a #6366f1...")

    # Leer el archivo actual
    with open("templates/login.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Cambiar background: white por background: #6366f1 en robot-section
    content = content.replace("background: white;", "background: #6366f1;")

    # Escribir el archivo actualizado
    with open("templates/login.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Color del panel izquierdo cambiado a #6366f1")


if __name__ == "__main__":
    simple_color_fix()
