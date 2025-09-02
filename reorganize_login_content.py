#!/usr/bin/env python3
"""
Script para reorganizar el contenido del login
"""


def reorganize_login_content():
    """Mueve el texto de bienvenida del panel izquierdo al panel derecho"""

    print("🔄 Reorganizando contenido del login...")

    # Leer el archivo actual
    with open("templates/login.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Eliminar el welcome-text del panel izquierdo
    welcome_text_to_remove = """        <div class="welcome-text">
          <h2>¡HOLA!</h2>
          <h3>Bienvenido</h3>
          <p>
            Estás a punto de acceder a MedConnect, donde podrás gestionar tu
            información clínica y permitir que tus familiares se mantengan
            informados sobre tu salud.
          </p>
        </div>"""

    content = content.replace(welcome_text_to_remove, "")

    # 2. Agregar el texto de bienvenida después del login-header
    header_section = """        <div class="login-header">
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

    new_header_section = """        <div class="login-header">
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
        </div>

        <div class="welcome-section" style="text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 16px;">
          <h2 style="color: var(--color-primary); font-size: 1.8em; font-weight: 700; margin-bottom: 10px;">¡HOLA!</h2>
          <h3 style="color: var(--color-secondary); font-size: 1.3em; font-weight: 500; margin-bottom: 15px;">Bienvenido</h3>
          <p style="color: var(--color-gray); font-size: 1em; line-height: 1.6;">
            Estás a punto de acceder a MedConnect, donde podrás gestionar tu
            información clínica y permitir que tus familiares se mantengan
            informados sobre tu salud.
          </p>
        </div>"""

    content = content.replace(header_section, new_header_section)

    # 3. Escribir el archivo actualizado
    with open("templates/login.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Contenido reorganizado:")
    print("   - Texto de bienvenida movido del panel izquierdo al derecho")
    print("   - Ubicado debajo del header MedConnect")
    print("   - Panel izquierdo solo con imágenes")


if __name__ == "__main__":
    reorganize_login_content()
