#!/usr/bin/env python3
"""
Script para cambiar el panel izquierdo a color sólido #6366f1
"""


def fix_panel_color_solid():
    """Cambia el panel izquierdo a color sólido #6366f1"""

    print("🎨 Cambiando panel izquierdo a color sólido #6366f1...")

    # Leer el archivo actual
    with open("templates/login.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Cambiar el panel izquierdo de gradiente a color sólido
    panel_gradient = """        .robot-section {
            flex: 1;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            position: relative;
        }"""

    panel_solid = """        .robot-section {
            flex: 1;
            background: #6366f1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            position: relative;
        }"""

    content = content.replace(panel_gradient, panel_solid)

    # Escribir el archivo actualizado
    with open("templates/login.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Panel izquierdo actualizado:")
    print("   - Panel izquierdo: color sólido #6366f1")
    print("   - Fondo del body: blanco")
    print("   - Container: blanco")
    print("   - Panel derecho: blanco")


if __name__ == "__main__":
    fix_panel_color_solid()
