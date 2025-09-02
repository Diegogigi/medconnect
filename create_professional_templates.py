#!/usr/bin/env python3
"""
Script para crear templates profesionales de login y register
"""


def create_professional_templates():
    """Crea templates profesionales que coincidan con la landing page"""

    print("🔧 Creando templates profesionales...")

    # Template de login profesional
    login_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedConnect - Iniciar Sesión</title>
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='images/favicon.ico') }}">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --color-primary: #0066cc;
            --color-secondary: #6366f1;
            --color-tertiary: #8b5cf6;
            --color-white: #ffffff;
            --color-gray: #6b7280;
            --color-light-gray: #f3f4f6;
            --color-error: #ef4444;
            --color-success: #10b981;
        }

        body {
            font-family: 'Inter', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .login-container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
            width: 100%;
            max-width: 450px;
            text-align: center;
        }

        .login-header {
            margin-bottom: 30px;
        }

        .login-header h1 {
            color: var(--color-primary);
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .login-header p {
            color: var(--color-gray);
            font-size: 1.1em;
            margin-bottom: 0;
        }

        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: var(--color-primary);
        }

        .form-group input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s ease;
            box-sizing: border-box;
        }

        .form-group input:focus {
            outline: none;
            border-color: var(--color-secondary);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }

        .btn-login {
            background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            width: 100%;
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s ease;
        }

        .btn-login:hover {
            transform: translateY(-2px);
        }

        .alert {
            padding: 15px;
            margin: 20px 0;
            border-radius: 10px;
            text-align: center;
        }

        .alert-error {
            background: #fef2f2;
            color: var(--color-error);
            border: 1px solid #fecaca;
        }

        .alert-success {
            background: #f0fdf4;
            color: var(--color-success);
            border: 1px solid #bbf7d0;
        }

        .demo-users {
            margin-top: 30px;
            padding: 20px;
            background: var(--color-light-gray);
            border-radius: 10px;
            text-align: left;
        }

        .demo-users h4 {
            color: var(--color-primary);
            margin-bottom: 15px;
            text-align: center;
        }

        .user-demo {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid var(--color-secondary);
        }

        .links {
            margin-top: 25px;
            text-align: center;
        }

        .links a {
            color: var(--color-secondary);
            text-decoration: none;
            font-weight: 500;
            margin: 0 10px;
        }

        .links a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1><i class="fas fa-heartbeat"></i> MedConnect</h1>
            <p>Accede a tu plataforma médica</p>
        </div>

        {% if message %}
        <div class="alert alert-{{ 'success' if success else 'error' }}">
            <i class="fas fa-{{ 'check-circle' if success else 'exclamation-triangle' }}"></i>
            {{ message }}
        </div>
        {% endif %}

        <form method="POST" action="/login">
            <div class="form-group">
                <label for="email">
                    <i class="fas fa-envelope"></i> Email
                </label>
                <input type="email" id="email" name="email" required placeholder="tu@email.com" />
            </div>

            <div class="form-group">
                <label for="password">
                    <i class="fas fa-lock"></i> Contraseña
                </label>
                <input type="password" id="password" name="password" required placeholder="Tu contraseña" />
            </div>

            <button type="submit" class="btn-login">
                <i class="fas fa-sign-in-alt"></i> Iniciar Sesión
            </button>
        </form>

        <div class="demo-users">
            <h4><i class="fas fa-users"></i> Usuarios de Prueba</h4>
            
            <div class="user-demo">
                <strong><i class="fas fa-user"></i> Paciente:</strong><br>
                Email: paciente@test.com<br>
                Contraseña: password123
            </div>

            <div class="user-demo">
                <strong><i class="fas fa-user-md"></i> Profesional:</strong><br>
                Email: diego.castro.lagos@gmail.com<br>
                Contraseña: password123
            </div>
        </div>

        <div class="links">
            <a href="/"><i class="fas fa-home"></i> Volver al inicio</a>
            <a href="/register"><i class="fas fa-user-plus"></i> Crear cuenta</a>
        </div>
    </div>
</body>
</html>"""

    # Escribir el nuevo login.html
    with open("templates/login.html", "w", encoding="utf-8") as f:
        f.write(login_html)

    print("✅ Login profesional creado")

    # Verificar que register.html ya existe y tiene buen contenido
    try:
        with open("templates/register.html", "r", encoding="utf-8") as f:
            register_content = f.read()

        if len(register_content) > 1000:  # Si es un template completo
            print("✅ Register.html ya existe y es completo")
        else:
            print("⚠️ Register.html existe pero es básico")
    except FileNotFoundError:
        print("❌ Register.html no encontrado")


if __name__ == "__main__":
    create_professional_templates()
