#!/usr/bin/env python3
"""
Script para arreglar la ruta index para mostrar interfaz web
"""

import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)


def fix_index_route():
    """Arregla la ruta index para mostrar interfaz web en lugar de JSON"""

    print("🔧 Arreglando ruta index para mostrar interfaz web...")

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar la función index
    old_index = """@app.route("/")
def index():
    # Si tienes templates, usa render_template("index.html")
    msg = "MedConnect API OK"
    if request.args.get("logout") == "success":
        msg += " - sesión cerrada."
    return jsonify({"status":"ok","message":msg,"time":datetime.now().isoformat()})"""

    new_index = '''@app.route("/")
def index():
    # Renderizar template HTML si existe, sino mostrar página básica
    if os.path.exists(os.path.join("templates", "index.html")):
        return render_template("index.html")
    else:
        # Página básica de bienvenida
        return """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MedConnect - Desarrollo Local</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; margin-bottom: 30px; }
                .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .btn { background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 5px; }
                .btn:hover { background: #0056b3; }
                .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 MedConnect</h1>
                    <p><strong>Modo:</strong> Desarrollo Local</p>
                </div>
                
                <div class="status">
                    <h3>✅ Aplicación Funcionando</h3>
                    <p>La aplicación está corriendo correctamente en modo desarrollo.</p>
                </div>
                
                <div class="section">
                    <h3>🔐 Acceso al Sistema</h3>
                    <p>Usuarios de prueba disponibles:</p>
                    <ul>
                        <li><strong>Paciente:</strong> paciente@test.com / password123</li>
                        <li><strong>Profesional:</strong> diego.castro.lagos@gmail.com / password123</li>
                    </ul>
                    <a href="/login" class="btn">Iniciar Sesión</a>
                </div>
                
                <div class="section">
                    <h3>🧪 Pruebas de API</h3>
                    <a href="/health" class="btn">Health Check</a>
                    <a href="/api/patient/1/consultations" class="btn">Consultas Paciente</a>
                    <a href="/api/patient/1/exams" class="btn">Exámenes Paciente</a>
                </div>
                
                <div class="section">
                    <h3>📊 Estado del Sistema</h3>
                    <p><strong>PostgreSQL:</strong> Modo fallback (datos simulados)</p>
                    <p><strong>Auth Manager:</strong> Funcionando</p>
                    <p><strong>Debug:</strong> Activado</p>
                </div>
            </div>
        </body>
        </html>
        """'''

    # Reemplazar en el contenido
    if old_index in content:
        content = content.replace(old_index, new_index)

        # Escribir el archivo actualizado
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Ruta index actualizada para mostrar interfaz web")
        print("🌐 Ahora puedes ver la interfaz en http://localhost:5000")
    else:
        print("❌ No se encontró la función index original")
        print("   Verifica que el archivo app.py tenga la función index correcta")


if __name__ == "__main__":
    fix_index_route()
