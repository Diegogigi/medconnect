#!/usr/bin/env python3
"""
Script para integrar las imágenes oficiales en los templates
"""


def integrate_official_images():
    """Integra las imágenes oficiales en los templates"""

    print("🖼️ Integrando imágenes oficiales en templates...")

    # 1. Actualizar login.html para usar las imágenes oficiales
    print("\n1️⃣ Actualizando login.html...")

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
            --color-accent: #a855f7;
            --color-white: #ffffff;
            --color-gray: #6b7280;
            --color-light-gray: #f8fafc;
            --color-success: #10b981;
            --color-error: #ef4444;
            
            --gradient-bg: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            --gradient-card: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            --gradient-button: linear-gradient(135deg, var(--color-secondary) 0%, var(--color-tertiary) 100%);
        }

        body {
            font-family: 'Inter', Arial, sans-serif;
            background: var(--gradient-bg);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .login-wrapper {
            display: flex;
            background: white;
            border-radius: 24px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            max-width: 1000px;
            width: 100%;
            min-height: 600px;
        }

        .login-left {
            flex: 1;
            background: linear-gradient(135deg, var(--color-secondary) 0%, var(--color-tertiary) 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
            padding: 40px;
        }

        .logo-container {
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
        }

        .welcome-text h2 {
            font-size: 2.2em;
            font-weight: 700;
            margin-bottom: 15px;
        }

        .welcome-text h3 {
            font-size: 1.5em;
            font-weight: 500;
            margin-bottom: 15px;
            opacity: 0.9;
        }

        .welcome-text p {
            font-size: 1.1em;
            opacity: 0.8;
            line-height: 1.6;
            max-width: 300px;
        }

        .login-right {
            flex: 1;
            padding: 60px 50px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .login-header {
            text-align: center;
            margin-bottom: 40px;
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
        }

        .form-group {
            margin-bottom: 25px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: var(--color-primary);
            font-size: 14px;
        }

        .input-wrapper {
            position: relative;
        }

        .input-wrapper i {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--color-gray);
            font-size: 16px;
        }

        .form-group input {
            width: 100%;
            padding: 15px 15px 15px 45px;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: #fafafa;
        }

        .form-group input:focus {
            outline: none;
            border-color: var(--color-secondary);
            background: white;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }

        .btn-login {
            background: var(--gradient-button);
            color: white;
            padding: 16px 30px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            width: 100%;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            margin-bottom: 15px;
        }

        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);
        }

        .btn-register {
            background: linear-gradient(135deg, var(--color-tertiary) 0%, var(--color-accent) 100%);
            color: white;
            padding: 16px 30px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            width: 100%;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .btn-register:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(168, 85, 247, 0.3);
        }

        .alert {
            padding: 15px;
            margin: 20px 0;
            border-radius: 12px;
            text-align: center;
            font-weight: 500;
        }

        .alert-error {
            background: #fef2f2;
            color: var(--color-error);
            border: 2px solid #fecaca;
        }

        .alert-success {
            background: #f0fdf4;
            color: var(--color-success);
            border: 2px solid #bbf7d0;
        }

        .demo-users {
            background: var(--color-light-gray);
            border-radius: 12px;
            padding: 20px;
            margin-top: 25px;
        }

        .demo-users h4 {
            color: var(--color-primary);
            margin-bottom: 15px;
            text-align: center;
            font-size: 16px;
        }

        .user-demo {
            background: white;
            padding: 12px 15px;
            border-radius: 8px;
            margin-bottom: 8px;
            border-left: 4px solid var(--color-secondary);
            font-size: 14px;
        }

        .links {
            text-align: center;
            margin-top: 30px;
        }

        .links a {
            color: var(--color-secondary);
            text-decoration: none;
            font-weight: 500;
            margin: 0 15px;
            font-size: 14px;
        }

        .links a:hover {
            text-decoration: underline;
        }

        .forgot-password {
            text-align: center;
            margin: 15px 0;
        }

        .forgot-password a {
            color: var(--color-gray);
            text-decoration: none;
            font-size: 14px;
        }

        .forgot-password a:hover {
            color: var(--color-secondary);
        }

        /* Responsive */
        @media (max-width: 768px) {
            .login-wrapper {
                flex-direction: column;
                margin: 10px;
            }
            
            .login-left {
                min-height: 250px;
                padding: 30px;
            }
            
            .logo-image, .ai-image {
                width: 80px;
                height: 80px;
            }
            
            .welcome-text h2 {
                font-size: 1.8em;
            }
            
            .login-right {
                padding: 40px 30px;
            }
        }
    </style>
</head>
<body>
    <div class="login-wrapper">
        <!-- Panel izquierdo con imágenes oficiales -->
        <div class="login-left">
            <div class="logo-container">
                <img src="{{ url_for('static', filename='images/logo.png') }}" 
                     alt="MedConnect Logo" 
                     class="logo-image">
            </div>
            
            <div class="ai-image-container">
                <img src="{{ url_for('static', filename='images/Imagen2.png') }}" 
                     alt="IA MedConnect" 
                     class="ai-image">
            </div>
            
            <div class="welcome-text">
                <h2>¡HOLA!</h2>
                <h3>Bienvenido</h3>
                <p>Estás a punto de acceder a MedConnect, donde podrás gestionar tu información clínica y permitir que tus familiares se mantengan informados sobre tu salud.</p>
            </div>
        </div>

        <!-- Panel derecho con formulario -->
        <div class="login-right">
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
                    <label for="email">Nombre de Usuario</label>
                    <div class="input-wrapper">
                        <i class="fas fa-user"></i>
                        <input type="email" id="email" name="email" required placeholder="tu@email.com" />
                    </div>
                </div>

                <div class="form-group">
                    <label for="password">Contraseña</label>
                    <div class="input-wrapper">
                        <i class="fas fa-lock"></i>
                        <input type="password" id="password" name="password" required placeholder="Tu contraseña" />
                    </div>
                </div>

                <div class="forgot-password">
                    <a href="#">¿Has olvidado tu contraseña?</a>
                </div>

                <button type="submit" class="btn-login">
                    Ingresar
                </button>

                <button type="button" class="btn-register" onclick="window.location.href='/register'">
                    Crear Cuenta
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
            </div>
        </div>
    </div>
</body>
</html>"""

    # Escribir el login.html actualizado
    with open("templates/login.html", "w", encoding="utf-8") as f:
        f.write(login_html)

    print("✅ Login actualizado con imágenes oficiales")

    # 2. Actualizar register.html también
    print("\n2️⃣ Actualizando register.html...")

    register_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedConnect - Crear Cuenta</title>
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
            --color-accent: #a855f7;
            --color-white: #ffffff;
            --color-gray: #6b7280;
            --color-light-gray: #f8fafc;
            --color-success: #10b981;
            --color-error: #ef4444;
            
            --gradient-bg: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            --gradient-button: linear-gradient(135deg, var(--color-secondary) 0%, var(--color-tertiary) 100%);
        }

        body {
            font-family: 'Inter', Arial, sans-serif;
            background: var(--gradient-bg);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .register-wrapper {
            display: flex;
            background: white;
            border-radius: 24px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            max-width: 1200px;
            width: 100%;
            min-height: 700px;
        }

        .register-left {
            flex: 1;
            background: linear-gradient(135deg, var(--color-secondary) 0%, var(--color-tertiary) 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px;
        }

        .logo-container {
            text-align: center;
            color: white;
            margin-bottom: 20px;
        }

        .logo-image {
            width: 100px;
            height: 100px;
            object-fit: contain;
            margin-bottom: 15px;
            border-radius: 15px;
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
        }

        .ai-image {
            width: 180px;
            height: 180px;
            object-fit: contain;
            border-radius: 20px;
            margin-bottom: 20px;
        }

        .welcome-text h2 {
            font-size: 2em;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .welcome-text h3 {
            font-size: 1.3em;
            font-weight: 500;
            margin-bottom: 15px;
            opacity: 0.9;
        }

        .welcome-text p {
            font-size: 1em;
            opacity: 0.8;
            line-height: 1.5;
            max-width: 280px;
        }

        .register-right {
            flex: 1.2;
            padding: 40px 50px;
            overflow-y: auto;
        }

        .register-header {
            text-align: center;
            margin-bottom: 30px;
        }

        .register-header h1 {
            color: var(--color-primary);
            font-size: 2.2em;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .register-header p {
            color: var(--color-gray);
            font-size: 1em;
        }

        .form-row {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }

        .form-group {
            flex: 1;
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 6px;
            font-weight: 600;
            color: var(--color-primary);
            font-size: 14px;
        }

        .input-wrapper {
            position: relative;
        }

        .input-wrapper i {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--color-gray);
            font-size: 14px;
        }

        .form-group input, .form-group select {
            width: 100%;
            padding: 12px 12px 12px 40px;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            font-size: 14px;
            transition: all 0.3s ease;
            background: #fafafa;
        }

        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: var(--color-secondary);
            background: white;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }

        .user-type-selector {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
        }

        .user-type-option {
            flex: 1;
            padding: 15px;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: #fafafa;
        }

        .user-type-option:hover {
            border-color: var(--color-secondary);
            background: white;
        }

        .user-type-option.selected {
            border-color: var(--color-secondary);
            background: rgba(99, 102, 241, 0.1);
        }

        .user-type-option i {
            font-size: 24px;
            color: var(--color-secondary);
            margin-bottom: 8px;
        }

        .btn-register-main {
            background: var(--gradient-button);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            width: 100%;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }

        .btn-register-main:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);
        }

        .links {
            text-align: center;
            margin-top: 25px;
        }

        .links a {
            color: var(--color-secondary);
            text-decoration: none;
            font-weight: 500;
            margin: 0 15px;
            font-size: 14px;
        }

        .links a:hover {
            text-decoration: underline;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .register-wrapper {
                flex-direction: column;
                margin: 10px;
            }
            
            .register-left {
                min-height: 200px;
                padding: 25px;
            }
            
            .logo-image, .ai-image {
                width: 60px;
                height: 60px;
            }
            
            .welcome-text h2 {
                font-size: 1.5em;
            }
            
            .register-right {
                padding: 30px 25px;
            }
            
            .form-row {
                flex-direction: column;
                gap: 0;
            }
        }
    </style>
</head>
<body>
    <div class="register-wrapper">
        <!-- Panel izquierdo con imágenes oficiales -->
        <div class="register-left">
            <div class="logo-container">
                <img src="{{ url_for('static', filename='images/logo.png') }}" 
                     alt="MedConnect Logo" 
                     class="logo-image">
            </div>
            
            <div class="ai-image-container">
                <img src="{{ url_for('static', filename='images/Imagen2.png') }}" 
                     alt="IA MedConnect" 
                     class="ai-image">
            </div>
            
            <div class="welcome-text">
                <h2>¡Únete!</h2>
                <h3>Crear Cuenta</h3>
                <p>Regístrate en MedConnect y accede a una plataforma integral de gestión médica familiar con IA inteligente.</p>
            </div>
        </div>

        <!-- Panel derecho con formulario -->
        <div class="register-right">
            <div class="register-header">
                <h1><i class="fas fa-heartbeat"></i> MedConnect</h1>
                <p>Crear nueva cuenta</p>
            </div>

            {% if message %}
            <div class="alert alert-{{ 'success' if success else 'error' }}">
                <i class="fas fa-{{ 'check-circle' if success else 'exclamation-triangle' }}"></i>
                {{ message }}
            </div>
            {% endif %}

            <form method="POST" action="/register">
                <!-- Selector de tipo de usuario -->
                <div class="form-group">
                    <label>Tipo de Usuario</label>
                    <div class="user-type-selector">
                        <div class="user-type-option selected" onclick="selectUserType('paciente', this)">
                            <i class="fas fa-user"></i>
                            <div><strong>Paciente</strong></div>
                            <div style="font-size: 12px; color: var(--color-gray);">Gestiona tu salud</div>
                        </div>
                        <div class="user-type-option" onclick="selectUserType('profesional', this)">
                            <i class="fas fa-user-md"></i>
                            <div><strong>Profesional</strong></div>
                            <div style="font-size: 12px; color: var(--color-gray);">Atiende pacientes</div>
                        </div>
                    </div>
                    <input type="hidden" id="tipo_usuario" name="tipo_usuario" value="paciente">
                </div>

                <!-- Datos personales -->
                <div class="form-row">
                    <div class="form-group">
                        <label for="nombre">Nombre</label>
                        <div class="input-wrapper">
                            <i class="fas fa-user"></i>
                            <input type="text" id="nombre" name="nombre" required placeholder="Tu nombre" />
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="apellido">Apellido</label>
                        <div class="input-wrapper">
                            <i class="fas fa-user"></i>
                            <input type="text" id="apellido" name="apellido" required placeholder="Tu apellido" />
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <label for="email">Email</label>
                    <div class="input-wrapper">
                        <i class="fas fa-envelope"></i>
                        <input type="email" id="email" name="email" required placeholder="tu@email.com" />
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="password">Contraseña</label>
                        <div class="input-wrapper">
                            <i class="fas fa-lock"></i>
                            <input type="password" id="password" name="password" required placeholder="Mínimo 6 caracteres" />
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="confirm_password">Confirmar</label>
                        <div class="input-wrapper">
                            <i class="fas fa-lock"></i>
                            <input type="password" id="confirm_password" name="confirm_password" required placeholder="Repetir contraseña" />
                        </div>
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="telefono">Teléfono</label>
                        <div class="input-wrapper">
                            <i class="fas fa-phone"></i>
                            <input type="tel" id="telefono" name="telefono" placeholder="+56 9 1234 5678" />
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="ciudad">Ciudad</label>
                        <div class="input-wrapper">
                            <i class="fas fa-map-marker-alt"></i>
                            <input type="text" id="ciudad" name="ciudad" placeholder="Tu ciudad" />
                        </div>
                    </div>
                </div>

                <button type="submit" class="btn-register-main">
                    <i class="fas fa-user-plus"></i> Crear Cuenta
                </button>
            </form>

            <div class="links">
                <a href="/login"><i class="fas fa-sign-in-alt"></i> Ya tengo cuenta</a>
                <a href="/"><i class="fas fa-home"></i> Volver al inicio</a>
            </div>
        </div>
    </div>

    <script>
        function selectUserType(type, element) {
            // Remover selección anterior
            document.querySelectorAll('.user-type-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            
            // Seleccionar nuevo tipo
            element.classList.add('selected');
            document.getElementById('tipo_usuario').value = type;
        }
    </script>
</body>
</html>"""

    # Escribir el register.html actualizado
    with open("templates/register.html", "w", encoding="utf-8") as f:
        f.write(register_html)

    print("✅ Register actualizado con imágenes oficiales")

    print("\n" + "=" * 50)
    print("🎨 TEMPLATES ACTUALIZADOS CON IMÁGENES OFICIALES:")
    print("✅ Login: logo.png + Imagen2.png + diseño moderno")
    print("✅ Register: logo.png + Imagen2.png + formulario completo")
    print("✅ Colores: Primarios y secundarios personalizados")
    print("✅ Responsive: Adaptable a móviles")


if __name__ == "__main__":
    integrate_official_images()
