#!/usr/bin/env python3
"""
Script para cambiar el fondo del body a blanco
"""


def fix_body_background():
    """Cambia el fondo del body a blanco"""

    print("⚪ Cambiando fondo del body a blanco...")

    # Leer el archivo actual
    with open("templates/login.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Cambiar el fondo del body a blanco
    content = content.replace(
        "background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);",
        "background: white;",
    )

    # Escribir el archivo actualizado
    with open("templates/login.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Fondo del body corregido:")
    print("   - Body: blanco")
    print("   - Panel izquierdo: gradiente #6366f1 a #8b5cf6")
    print("   - Container: blanco")
    print("   - Panel derecho: blanco")


if __name__ == "__main__":
    fix_body_background()
