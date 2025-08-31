#!/usr/bin/env python3
"""
Script para simplificar la función index
"""


def fix_index_simple():
    """Simplifica la función index para evitar errores"""

    print("🔧 Simplificando función index...")

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar la función index actual
    start_marker = '@app.route("/")\ndef index():'

    if start_marker in content:
        # Encontrar el inicio de la función
        start_pos = content.find(start_marker)

        # Encontrar el final de la función (buscar la siguiente función)
        next_function_markers = [
            "\n# ---------- AUTH ----------",
            '\n@app.route("/login"',
            '\n@app.route("/patient"',
            '\n@app.route("/professional"',
        ]

        end_pos = len(content)
        for marker in next_function_markers:
            pos = content.find(marker, start_pos)
            if pos != -1 and pos < end_pos:
                end_pos = pos

        # Reemplazar la función completa
        old_function = content[start_pos:end_pos]

        new_function = '''@app.route("/")
def index():
    # Página simple de bienvenida para desarrollo
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MedConnect - Desarrollo Local</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #f0f0f0; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
            .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 MedConnect</h1>
            <p><strong>Modo:</strong> Desarrollo Local</p>
            <p>✅ Aplicación funcionando correctamente</p>
            
            <h3>🔐 Acceso:</h3>
            <p>Usuarios de prueba:</p>
            <ul>
                <li>Paciente: paciente@test.com / password123</li>
                <li>Profesional: diego.castro.lagos@gmail.com / password123</li>
            </ul>
            <a href="/login" class="btn">Iniciar Sesión</a>
            
            <h3>🧪 Pruebas:</h3>
            <a href="/health" class="btn">Health Check</a>
            <a href="/api/patient/1/consultations" class="btn">API Consultas</a>
        </div>
    </body>
    </html>
    """
    return html'''

        # Reemplazar en el contenido
        content = content.replace(old_function, new_function)

        # Escribir el archivo actualizado
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Función index simplificada")
        print("🌐 Ahora deberías poder ver la interfaz en http://localhost:5000")
    else:
        print("❌ No se encontró la función index")


if __name__ == "__main__":
    fix_index_simple()
