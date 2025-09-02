#!/usr/bin/env python3
"""
Script para limpiar el diseño del login según las especificaciones
"""


def clean_login_design():
    """Limpia el diseño del login eliminando elementos innecesarios"""

    print("🧹 Limpiando diseño del login...")

    # Leer el archivo actual
    with open("templates/login.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Eliminar el logo del header (panel derecho)
    header_with_logo = """        <div class="login-header">
          <img
            src="{{ url_for('static', filename='images/logo.png') }}"
            alt="MedConnect Logo"
            style="
              width: 80px;
              height: 80px;
              object-fit: contain;
              margin-bottom: 15px;
              border-radius: 12px;
            "
          />
          <h1>MedConnect</h1>
          <p>Accede a tu plataforma médica</p>
        </div>"""

    header_clean = """        <div class="login-header">
          <h1>MedConnect</h1>
          <p>Accede a tu plataforma médica</p>
        </div>"""

    content = content.replace(header_with_logo, header_clean)

    # 2. Eliminar toda la sección de bienvenida
    welcome_section = """        <div
          class="welcome-section"
          style="
            text-align: left;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border-radius: 16px;
          "
        >
          <h2
            style="
              color: var(--color-primary);
              font-size: 1.8em;
              font-weight: 700;
              margin-bottom: 10px;
            "
          >
            ¡HOLA!
          </h2>
          <h3
            style="
              color: var(--color-secondary);
              font-size: 1.3em;
              font-weight: 500;
              margin-bottom: 15px;
            "
          >
            Bienvenido
          </h3>
          <p style="color: var(--color-gray); font-size: 1em; line-height: 1.6">
            Estás a punto de acceder a MedConnect, donde podrás gestionar tu
            información clínica y permitir que tus familiares se mantengan
            informados sobre tu salud.
          </p>
        </div>"""

    content = content.replace(welcome_section, "")

    # 3. Eliminar el logo del panel izquierdo y ajustar Imagen2.png
    left_panel_with_logo = """      <div class="login-left">
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
        </div>"""

    left_panel_clean = """      <div class="login-left">
        <div class="ai-image-container" style="display: flex; align-items: center; justify-content: center; height: 100%;">
          <img
            src="{{ url_for('static', filename='images/Imagen2.png') }}"
            alt="IA MedConnect"
            style="width: 100%; height: 100%; object-fit: cover; border-radius: 0;"
          />
        </div>"""

    content = content.replace(left_panel_with_logo, left_panel_clean)

    # 4. Eliminar los estilos CSS innecesarios
    css_to_remove = """      .logo-container {
        text-align: center;
        color: white;
        margin-bottom: 30px;
      }

      .logo-image {
        width: 120px;
        height: 120px;
        object-fit: contain;
        margin-bottom: 20px;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
      }

      .ai-image {
        width: 200px;
        height: 200px;
        object-fit: contain;
        border-radius: 20px;
        margin-bottom: 20px;
      }"""

    content = content.replace(css_to_remove, "")

    # Escribir el archivo actualizado
    with open("templates/login.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Diseño limpiado:")
    print("   - Texto de bienvenida eliminado")
    print("   - Logo.png eliminado del header")
    print("   - Imagen2.png agrandada y cuadrada con panel morado")
    print("   - CSS innecesario eliminado")


if __name__ == "__main__":
    clean_login_design()
