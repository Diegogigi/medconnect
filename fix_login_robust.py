#!/usr/bin/env python3
"""
Script para hacer la función de login más robusta
"""


def fix_login_robust():
    """Hace la función de login más robusta con fallback HTML"""

    print("🔧 Mejorando función de login con fallback robusto...")

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar la función login
    old_login = """@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return (
            render_template("login.html")
            if os.path.exists(os.path.join("templates", "login.html"))
            else "Login"
        )

    data = request.form or request.get_json(silent=True) or {}
    email, password = data.get("email", "").strip(), data.get("password", "")
    try:
        if not auth_manager:
            raise RuntimeError("AuthManager no disponible")
        ok, user_data = auth_manager.login_user(email, password)
        if not ok:
            return (
                render_template(
                    "login.html", message="Credenciales inválidas", success=False
                )
                if os.path.exists(os.path.join("templates", "login.html"))
                else (jsonify({"error": "Credenciales inválidas"}), 401)
            )
        # set session
        session.clear()
        session["user_id"] = user_data["id"]
        session["user_email"] = user_data["email"]
        session["user_name"] = user_data.get("nombre") or user_data.get("name") or email
        session["user_type"] = user_data.get("tipo_usuario", "paciente")
        if session["user_type"] == "profesional":
            return redirect(url_for("professional_dashboard"))
        return redirect(url_for("patient_dashboard"))

    except Exception as e:
        diag = diagnose_login_error(e)
        logger.error(f"[LOGIN] {diag['debug_info']}")
        return (
            render_template("login.html", message=diag["user_message"], success=False)
            if os.path.exists(os.path.join("templates", "login.html"))
            else (jsonify({"error": diag["user_message"]}), 500)
        )"""

    new_login = '''@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        try:
            return render_template("login.html")
        except Exception as e:
            logger.error(f"❌ Error cargando template login.html: {e}")
            return _login_fallback_html()
    
    data = request.form or request.get_json(silent=True) or {}
    email, password = data.get("email", "").strip(), data.get("password", "")
    
    try:
        if not auth_manager:
            raise RuntimeError("AuthManager no disponible")
        
        ok, user_data = auth_manager.login_user(email, password)
        if not ok:
            try:
                return render_template("login.html", message="Credenciales inválidas", success=False)
            except Exception as e:
                logger.error(f"❌ Error renderizando login con error: {e}")
                return _login_fallback_html("Credenciales inválidas", False)
        
        # set session
        session.clear()
        session["user_id"] = user_data["id"]
        session["user_email"] = user_data["email"]
        session["user_name"] = user_data.get("nombre") or user_data.get("name") or email
        session["user_type"] = user_data.get("tipo_usuario", "paciente")
        
        if session["user_type"] == "profesional":
            return redirect(url_for("professional_dashboard"))
        return redirect(url_for("patient_dashboard"))

    except Exception as e:
        diag = diagnose_login_error(e)
        logger.error(f"[LOGIN] {diag['debug_info']}")
        try:
            return render_template("login.html", message=diag["user_message"], success=False)
        except Exception as template_error:
            logger.error(f"❌ Error renderizando login con error: {template_error}")
            return _login_fallback_html(diag["user_message"], False)

def _login_fallback_html(message=None, success=True):
    """HTML de fallback para login"""
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
        <title>MedConnect - Login</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                max-width: 400px;
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
            .form-group input {{
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
            .btn:hover {{
                background: #0056b3;
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
            .demo-users {{
                margin-top: 20px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 MedConnect</h1>
                <p>Iniciar Sesión</p>
            </div>

            {alert_html}

            <form method="POST" action="/login">
                <div class="form-group">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" required />
                </div>

                <div class="form-group">
                    <label for="password">Contraseña:</label>
                    <input type="password" id="password" name="password" required />
                </div>

                <button type="submit" class="btn">Iniciar Sesión</button>
            </form>

            <div class="demo-users">
                <h4>👥 Usuarios de Prueba:</h4>
                <p>
                    <strong>Paciente:</strong><br />
                    Email: paciente@test.com<br />
                    Contraseña: password123
                </p>

                <p>
                    <strong>Profesional:</strong><br />
                    Email: diego.castro.lagos@gmail.com<br />
                    Contraseña: password123
                </p>
            </div>

            <p style="text-align: center; margin-top: 20px">
                <a href="/">← Volver al inicio</a>
            </p>
        </div>
    </body>
    </html>
    """
    return html'''

    # Reemplazar en el contenido
    if old_login in content:
        content = content.replace(old_login, new_login)

        # Escribir el archivo actualizado
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Función de login mejorada con fallback robusto")
        print("🔧 Incluye HTML completo si el template falla")
    else:
        print("❌ No se encontró la función login actual")


if __name__ == "__main__":
    fix_login_robust()
