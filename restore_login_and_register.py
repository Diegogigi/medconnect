#!/usr/bin/env python3
"""
Script para restaurar login original y añadir función register
"""


def restore_login_and_register():
    """Restaura login original y añade función register"""

    print("🔧 Restaurando login original y añadiendo register...")

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Buscar donde insertar la función register (después de login)
    login_end = """        except Exception as template_error:
            logger.error(f"❌ Error renderizando login con error: {template_error}")
            return _login_fallback_html(diag["user_message"], False)"""

    register_function = '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro de usuarios"""
    if request.method == 'GET':
        try:
            return render_template("register.html")
        except Exception as e:
            logger.error(f"❌ Error cargando template register.html: {e}")
            return _register_fallback_html()
    
    try:
        # Obtener datos del formulario
        user_data = {
            'email': request.form.get('email', '').strip().lower(),
            'password': request.form.get('password', ''),
            'nombre': request.form.get('nombre', '').strip(),
            'apellido': request.form.get('apellido', '').strip(),
            'telefono': request.form.get('telefono', '').strip(),
            'fecha_nacimiento': request.form.get('fecha_nacimiento', ''),
            'genero': request.form.get('genero', ''),
            'direccion': request.form.get('direccion', '').strip(),
            'ciudad': request.form.get('ciudad', '').strip(),
            'tipo_usuario': request.form.get('tipo_usuario', 'paciente').strip()
        }
        
        # Validar confirmación de contraseña
        confirm_password = request.form.get('confirm_password', '')
        if user_data['password'] != confirm_password:
            try:
                return render_template('register.html', 
                                     message='Las contraseñas no coinciden', 
                                     success=False, 
                                     user_data=user_data)
            except Exception:
                return _register_fallback_html('Las contraseñas no coinciden', False)
        
        # Registrar usuario usando AuthManager
        if not auth_manager:
            raise RuntimeError("AuthManager no disponible")
        
        success, message = auth_manager.register_user(user_data)
        
        if success:
            try:
                return render_template('register.html', 
                                     message='Usuario registrado exitosamente. Puedes iniciar sesión.', 
                                     success=True)
            except Exception:
                return _register_fallback_html('Usuario registrado exitosamente. Puedes iniciar sesión.', True)
        else:
            try:
                return render_template('register.html', 
                                     message=message, 
                                     success=False, 
                                     user_data=user_data)
            except Exception:
                return _register_fallback_html(message, False)
            
    except Exception as e:
        logger.error(f"[REGISTER] Error: {e}")
        try:
            return render_template('register.html', 
                                 message='Error interno del servidor. Inténtalo más tarde.', 
                                 success=False)
        except Exception:
            return _register_fallback_html('Error interno del servidor. Inténtalo más tarde.', False)

def _register_fallback_html(message=None, success=True):
    """HTML de fallback para register"""
    alert_html = ""
    if message:
        alert_class = "success" if success else "error"
        alert_html = f'<div class="alert alert-{alert_class}">{message}</div>'
    
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MedConnect - Registro</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                max-width: 600px;
                margin: 50px auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            .form-group label {{
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }}
            .form-group input, .form-group select {{
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }}
            .btn {{
                background: #007bff;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                width: 100%;
                font-size: 16px;
            }}
            .alert {{
                padding: 10px;
                margin: 10px 0;
                border-radius: 4px;
            }}
            .alert-error {{
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }}
            .alert-success {{
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 MedConnect</h1>
                <p>Crear Nueva Cuenta</p>
            </div>

            {alert_html}

            <form method="POST" action="/register">
                <div class="form-group">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" required />
                </div>
                
                <div class="form-group">
                    <label for="password">Contraseña:</label>
                    <input type="password" id="password" name="password" required />
                </div>
                
                <div class="form-group">
                    <label for="confirm_password">Confirmar Contraseña:</label>
                    <input type="password" id="confirm_password" name="confirm_password" required />
                </div>
                
                <div class="form-group">
                    <label for="nombre">Nombre:</label>
                    <input type="text" id="nombre" name="nombre" required />
                </div>
                
                <div class="form-group">
                    <label for="apellido">Apellido:</label>
                    <input type="text" id="apellido" name="apellido" required />
                </div>
                
                <div class="form-group">
                    <label for="tipo_usuario">Tipo de Usuario:</label>
                    <select id="tipo_usuario" name="tipo_usuario" required>
                        <option value="paciente">Paciente</option>
                        <option value="profesional">Profesional de la Salud</option>
                    </select>
                </div>

                <button type="submit" class="btn">Crear Cuenta</button>
            </form>

            <p style="text-align: center; margin-top: 20px">
                ¿Ya tienes cuenta? <a href="/login">Iniciar Sesión</a>
            </p>
            
            <p style="text-align: center; margin-top: 10px">
                <a href="/">← Volver al inicio</a>
            </p>
        </div>
    </body>
    </html>
    """
    return html'''

    # Insertar la función register después del login
    if login_end in content:
        content = content.replace(login_end, login_end + register_function)

        # Escribir el archivo actualizado
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Función register añadida exitosamente")
        print("🔧 Incluye template register.html y fallback")
    else:
        print("❌ No se encontró el punto de inserción")


if __name__ == "__main__":
    restore_login_and_register()
