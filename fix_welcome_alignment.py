#!/usr/bin/env python3
"""
Script para cambiar alineamiento del texto de bienvenida
"""


def fix_welcome_alignment():
    """Cambia el alineamiento del texto de bienvenida de centrado a izquierda"""

    print("🔧 Cambiando alineamiento del texto de bienvenida...")

    # Leer el archivo actual
    with open("templates/login.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Cambiar text-align: center por text-align: left
    content = content.replace("text-align: center;", "text-align: left;")

    # Escribir el archivo actualizado
    with open("templates/login.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Alineamiento cambiado:")
    print("   - Texto de bienvenida ahora alineado a la izquierda")
    print("   - Diseño más natural y legible")


if __name__ == "__main__":
    fix_welcome_alignment()
