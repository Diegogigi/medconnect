#!/usr/bin/env python3
"""
🚀 APP MINIMAL FUNCIONAL - Versión que SÍ funciona
"""

# ===== IMPORTS BÁSICOS =====
from flask import Flask, render_template, request, redirect, url_for, session, make_response
from functools import wraps
import os

# ===== CREAR APP FLASK =====
print("🔧 Creando aplicación Flask...")
app = Flask(__name__)
app.secret_key = 'medconnect-secret-key-2024'

# ===== CONFIGURACIÓN BÁSICA =====
print("⚙️ Configurando aplicación...")

# Configurar CORS si está disponible
try:
    from flask_cors import CORS
    CORS(app)
    print("✅ CORS configurado")
except ImportError:
    print("⚠️ CORS no disponible")

# ===== DECORADOR LOGIN_REQUIRED =====
def login_required(f):
    """Decorador simple para rutas protegidas"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ===== RUTAS PRINCIPALES =====
print("🛣️ Registrando rutas principales...")

@app.route('/')
def index():
    """Página principal"""
    print("📍 Acceso a página principal")
    user_data = session.get('user_data', {})
    
    try:
        return render_template('index.html', user=user_data)
    except Exception as e:
        print(f"⚠️ Error renderizando template: {e}")
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MedConnect - Página Principal</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; text-align: center; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .btn {{ background-color: #007bff; color: white; padding: 10px 20px; 
                       text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px; }}
                .btn:hover {{ background-color: #0056b3; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏥 MedConnect</h1>
                <p>¡Bienvenido a MedConnect! La plataforma está funcionando correctamente.</p>
                <div>
                    <a href="/login" class="btn">🔐 Iniciar Sesión</a>
                    <a href="/register" class="btn">📝 Registrarse</a>
                </div>
                <p><small>Usuario actual: {user_data.get('nombre', 'No autenticado')}</small></p>
            </div>
        </body>
        </html>
        """

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    print("🔐 Acceso a página de login")
    
    if request.method == 'GET':
        try:
            return render_template('login.html')
        except Exception as e:
            print(f"⚠️ Error renderizando login template: {e}")
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>MedConnect - Iniciar Sesión</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; text-align: center; }}
                    .container {{ max-width: 400px; margin: 0 auto; }}
                    .form-group {{ margin: 15px 0; text-align: left; }}
                    input {{ width: 100%; padding: 8px; margin: 5px 0; }}
                    .btn {{ background-color: #007bff; color: white; padding: 10px 20px; 
                           border: none; border-radius: 5px; cursor: pointer; width: 100%; }}
                    .btn:hover {{ background-color: #0056b3; }}
                    .links {{ margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔐 Iniciar Sesión</h1>
                    <form method="POST">
                        <div class="form-group">
                            <label>Email:</label>
                            <input type="email" name="email" required>
                        </div>
                        <div class="form-group">
                            <label>Contraseña:</label>
                            <input type="password" name="password" required>
                        </div>
                        <button type="submit" class="btn">Iniciar Sesión</button>
                    </form>
                    <div class="links">
                        <a href="/">← Volver al inicio</a> | 
                        <a href="/register">Registrarse</a>
                    </div>
                </div>
            </body>
            </html>
            """
    
    # POST - Procesar login
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    
    if not email or not password:
        return redirect(url_for('login'))
    
    # Simulación de login exitoso (para pruebas)
    print(f"🔑 Intento de login: {email}")
    session['user_id'] = 1
    session['user_email'] = email
    session['user_name'] = 'Usuario de Prueba'
    session['user_type'] = 'paciente'
    session['user_data'] = {
        'id': 1,
        'email': email,
        'nombre': 'Usuario',
        'apellido': 'de Prueba',
        'tipo_usuario': 'paciente'
    }
    
    return redirect(url_for('patient_dashboard'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    print("📝 Acceso a página de registro")
    
    if request.method == 'GET':
        try:
            return render_template('register.html')
        except Exception as e:
            print(f"⚠️ Error renderizando register template: {e}")
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>MedConnect - Registrarse</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; text-align: center; }}
                    .container {{ max-width: 400px; margin: 0 auto; }}
                    .form-group {{ margin: 15px 0; text-align: left; }}
                    input, select {{ width: 100%; padding: 8px; margin: 5px 0; }}
                    .btn {{ background-color: #28a745; color: white; padding: 10px 20px; 
                           border: none; border-radius: 5px; cursor: pointer; width: 100%; }}
                    .btn:hover {{ background-color: #1e7e34; }}
                    .links {{ margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📝 Registrarse</h1>
                    <form method="POST">
                        <div class="form-group">
                            <label>Nombre:</label>
                            <input type="text" name="nombre" required>
                        </div>
                        <div class="form-group">
                            <label>Apellido:</label>
                            <input type="text" name="apellido" required>
                        </div>
                        <div class="form-group">
                            <label>Email:</label>
                            <input type="email" name="email" required>
                        </div>
                        <div class="form-group">
                            <label>Contraseña:</label>
                            <input type="password" name="password" required>
                        </div>
                        <div class="form-group">
                            <label>Tipo de usuario:</label>
                            <select name="tipo_usuario">
                                <option value="paciente">Paciente</option>
                                <option value="profesional">Profesional</option>
                            </select>
                        </div>
                        <button type="submit" class="btn">Registrarse</button>
                    </form>
                    <div class="links">
                        <a href="/">← Volver al inicio</a> | 
                        <a href="/login">Iniciar Sesión</a>
                    </div>
                </div>
            </body>
            </html>
            """
    
    # POST - Procesar registro
    print("✅ Registro procesado (simulación)")
    return redirect(url_for('login'))

@app.route('/patient')
@login_required
def patient_dashboard():
    """Dashboard de paciente"""
    print("🏥 Acceso a dashboard de paciente")
    user_data = session.get('user_data', {})
    
    try:
        return render_template('patient.html', user=user_data) 
    except Exception as e:
        print(f"⚠️ Error renderizando patient template: {e}")
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MedConnect - Dashboard Paciente</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .btn {{ background-color: #dc3545; color: white; padding: 8px 15px; 
                       text-decoration: none; border-radius: 3px; }}
                .btn:hover {{ background-color: #c82333; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 Dashboard - Paciente</h1>
                    <p>Bienvenido, {user_data.get('nombre', 'Usuario')}!</p>
                    <p>Email: {user_data.get('email', 'No disponible')}</p>
                </div>
                <div>
                    <h2>Panel de Control</h2>
                    <p>Aquí podrás gestionar tus citas, ver tu historial médico y más.</p>
                    <a href="/logout" class="btn">Cerrar Sesión</a>
                </div>
            </div>
        </body>
        </html>
        """

@app.route('/professional')
@login_required
def professional_dashboard():
    """Dashboard de profesional"""
    print("👨‍⚕️ Acceso a dashboard de profesional")
    user_data = session.get('user_data', {})
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MedConnect - Dashboard Profesional</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .header {{ background-color: #e3f2fd; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
            .btn {{ background-color: #dc3545; color: white; padding: 8px 15px; 
                   text-decoration: none; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>👨‍⚕️ Dashboard - Profesional</h1>
                <p>Bienvenido, Dr. {user_data.get('nombre', 'Usuario')}!</p>
            </div>
            <div>
                <h2>Panel Profesional</h2>
                <p>Gestiona tus pacientes, agenda y consultas.</p>
                <a href="/logout" class="btn">Cerrar Sesión</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    print("👋 Cerrando sesión")
    session.clear()
    return redirect(url_for('index'))

# ===== RUTA DE PRUEBA =====
@app.route('/test')
def test():
    """Ruta de prueba"""
    return """
    <h1>🧪 Ruta de Prueba</h1>
    <p>Si ves esto, Flask está funcionando correctamente!</p>
    <a href="/">← Volver al inicio</a>
    """

# ===== FUNCIÓN MAIN =====
if __name__ == '__main__':
    print("🚀 INICIANDO MEDCONNECT MINIMAL...")
    print("=" * 50)
    
    # Mostrar rutas registradas
    print("🛣️ Rutas registradas:")
    for rule in app.url_map.iter_rules():
        print(f"  ✅ {rule.endpoint:20} -> {rule.rule}")
    
    print("=" * 50)
    print("🌐 Servidor iniciando en http://127.0.0.1:5000")
    print("✨ Todas las rutas principales deberían funcionar")
    
    app.run(host='127.0.0.1', port=5000, debug=True) 