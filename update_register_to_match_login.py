#!/usr/bin/env python3
"""
Script para actualizar el register con el mismo diseño del login
"""


def update_register_to_match_login():
    """Actualiza el register para que coincida con el diseño del login"""

    print("🔄 Actualizando register para que coincida con el login...")

    # Leer el archivo actual del register
    with open("templates/register.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Cambiar el fondo del body a #f8fafc (gris muy claro)
    content = content.replace("background: var(--gradient-bg);", "background: #f8fafc;")

    # 2. Cambiar el panel izquierdo a blanco
    content = content.replace(
        "background: linear-gradient(135deg, var(--color-secondary) 0%, var(--color-tertiary) 100%);",
        "background: white;",
    )

    # 3. Cambiar el container principal a blanco
    content = content.replace("background: white;", "background: white;")

    # 4. Cambiar el color del texto del panel izquierdo a oscuro (ya que ahora es blanco)
    content = content.replace("color: white;", "color: #1e293b;")

    # Escribir el archivo actualizado
    with open("templates/register.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Register actualizado:")
    print("   - Fondo: gris muy claro (#f8fafc)")
    print("   - Panel izquierdo: blanco")
    print("   - Container: blanco")
    print("   - Texto: oscuro para contraste")
    print("   - Mismo diseño minimalista que el login")


if __name__ == "__main__":
    update_register_to_match_login()
