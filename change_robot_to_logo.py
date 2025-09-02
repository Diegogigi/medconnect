#!/usr/bin/env python3
"""
Script para cambiar la imagen del robot por el logo grande
"""


def change_robot_to_logo():
    """Cambia la imagen del robot por el logo grande"""

    print("🔄 Cambiando imagen del robot por logo grande...")

    # Leer el archivo actual
    with open("templates/login.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Cambiar Imagen2.png por logo.png
    content = content.replace(
        "src=\"{{ url_for('static', filename='images/Imagen2.png') }}\"",
        "src=\"{{ url_for('static', filename='images/logo.png') }}\"",
    )

    # Cambiar el alt text también
    content = content.replace('alt="IA MedConnect"', 'alt="MedConnect Logo"')

    # Cambiar la clase CSS para ajustar el tamaño del logo
    content = content.replace(
        'class="robot-image"',
        'class="robot-image" style="width: 200px; height: 200px; object-fit: contain;"',
    )

    # Escribir el archivo actualizado
    with open("templates/login.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Imagen cambiada:")
    print("   - Robot IA reemplazado por logo grande")
    print("   - Tamaño ajustado para el logo")
    print("   - Alt text actualizado")


if __name__ == "__main__":
    change_robot_to_logo()
