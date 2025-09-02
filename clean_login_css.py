#!/usr/bin/env python3
"""
Script para limpiar CSS del login eliminando estilos de usuarios de prueba
"""


def clean_login_css():
    """Elimina estilos CSS innecesarios del login"""

    print("🧹 Limpiando CSS del login...")

    # Leer el archivo actual
    with open("templates/login.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Eliminar los estilos de demo-users y user-demo que ya no se usan
    lines_to_remove = [
        "      .demo-users {",
        "        background: var(--color-light-gray);",
        "        border-radius: 12px;",
        "        padding: 20px;",
        "        margin-top: 25px;",
        "      }",
        "",
        "      .demo-users h4 {",
        "        color: var(--color-primary);",
        "        margin-bottom: 15px;",
        "        text-align: center;",
        "        font-size: 16px;",
        "      }",
        "",
        "      .user-demo {",
        "        background: white;",
        "        padding: 12px 15px;",
        "        border-radius: 8px;",
        "        margin-bottom: 8px;",
        "        border-left: 4px solid var(--color-secondary);",
        "        font-size: 14px;",
        "      }",
        "",
    ]

    # Convertir a texto para eliminar
    text_to_remove = "\n".join(lines_to_remove)

    # Eliminar el texto
    content_cleaned = content.replace(text_to_remove, "")

    # Escribir archivo limpio
    with open("templates/login.html", "w", encoding="utf-8") as f:
        f.write(content_cleaned)

    print("✅ CSS del login limpiado - estilos innecesarios eliminados")


if __name__ == "__main__":
    clean_login_css()
