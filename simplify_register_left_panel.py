#!/usr/bin/env python3
"""
Script para simplificar el panel izquierdo del register dejando solo el logo
"""


def simplify_register_left_panel():
    """Simplifica el panel izquierdo del register dejando solo el logo"""

    print("🎯 Simplificando panel izquierdo del register...")

    # Leer el archivo actual
    with open("templates/register.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Reemplazar todo el contenido del panel izquierdo con solo el logo
    old_left_panel = """      <!-- Panel izquierdo con imágenes oficiales -->
      <div class="register-left">
        <div class="logo-container">
          <img
            src="{{ url_for('static', filename='images/logo.png') }}"
            alt="MedConnect Logo"
            class="logo-image"
          />
        </div>

        <div class="ai-image-container">
          <img
            src="{{ url_for('static', filename='images/Imagen2.png') }}"
            alt="IA MedConnect"
            class="ai-image"
          />
        </div>

        <div class="welcome-text">
          <h2>¡Únete!</h2>
          <h3>Crear Cuenta</h3>
          <p>
            Regístrate en MedConnect y accede a una plataforma integral de
            gestión médica familiar con IA inteligente.
          </p>
        </div>
      </div>"""

    new_left_panel = """      <!-- Panel izquierdo con logo -->
      <div class="register-left">
        <div class="logo-container">
          <img
            src="{{ url_for('static', filename='images/logo.png') }}"
            alt="MedConnect Logo"
            style="width: 250px; height: 250px; object-fit: contain;"
          />
        </div>
      </div>"""

    content = content.replace(old_left_panel, new_left_panel)

    # Escribir el archivo actualizado
    with open("templates/register.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Panel izquierdo simplificado:")
    print("   - Solo logo grande")
    print("   - Sin Imagen2.png")
    print("   - Sin texto de bienvenida")
    print("   - Igual que el login")


if __name__ == "__main__":
    simplify_register_left_panel()
