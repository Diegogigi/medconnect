#!/usr/bin/env python3
"""
Script para cambiar específicamente solo el fondo del body
"""


def fix_specific_background():
    """Cambia específicamente solo el fondo del body"""

    print("🎯 Cambiando específicamente solo el fondo del body...")

    # Leer el archivo actual
    with open("templates/login.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Cambiar SOLO el fondo del body, no el del panel izquierdo
    # Buscar la línea específica del body
    body_background = """        body {
            font-family: 'Inter', Arial, sans-serif;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }"""

    body_background_fixed = """        body {
            font-family: 'Inter', Arial, sans-serif;
            background: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }"""

    content = content.replace(body_background, body_background_fixed)

    # Escribir el archivo actualizado
    with open("templates/login.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Fondo del body corregido específicamente:")
    print("   - Body: blanco")
    print("   - Panel izquierdo: mantiene gradiente #6366f1 a #8b5cf6")
    print("   - Container: blanco")
    print("   - Panel derecho: blanco")


if __name__ == "__main__":
    fix_specific_background()
