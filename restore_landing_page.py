#!/usr/bin/env python3
"""
Script para restaurar la landing page original
"""

def restore_landing_page():
    """Restaura la landing page original"""
    
    print("🔧 Restaurando landing page original...")
    
    # Leer el archivo app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar y reemplazar la función index actual
    old_index = '''@app.route("/")
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
    
    new_index = '''@app.route("/")
def index():
    """Página principal - Landing page original"""
    return render_template("index.html")'''
    
    # Reemplazar en el contenido
    if old_index in content:
        content = content.replace(old_index, new_index)
        
        # Escribir el archivo actualizado
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Landing page original restaurada")
        print("🔧 Ahora usará templates/index.html")
    else:
        print("❌ No se encontró la función index actual")
        print("🔍 Verificando si ya está usando el template...")
        
        # Verificar si ya está usando render_template
        if 'render_template("index.html")' in content:
            print("✅ Ya está usando el template index.html")
        else:
            print("⚠️ Necesita configuración manual")

if __name__ == "__main__":
    restore_landing_page() 