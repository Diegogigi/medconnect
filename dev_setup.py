#!/usr/bin/env python3
"""
Script para configurar entorno de desarrollo con datos de prueba
"""

import os
import json

def setup_dev_environment():
    """Configura el entorno de desarrollo con datos de prueba"""
    
    print("🔧 Configurando entorno de desarrollo...")
    
    # Crear directorios necesarios
    directories = [
        "static",
        "static/css",
        "static/js", 
        "static/images",
        "static/uploads",
        "templates"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ Directorio creado: {directory}")
    
    # Crear archivo CSS básico si no existe
    css_file = "static/css/styles.css"
    if not os.path.exists(css_file):
        basic_css = """
/* Estilos básicos para desarrollo */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.btn {
    background: #007bff;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
}

.btn:hover {
    background: #0056b3;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

.form-group input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.alert {
    padding: 10px;
    margin: 10px 0;
    border-radius: 4px;
}

.alert-success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.alert-error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}
"""
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(basic_css)
        print(f"  ✅ Archivo CSS creado: {css_file}")
    
    # Crear template básico si no existe
    template_file = "templates/index.html"
    if not os.path.exists(template_file):
        basic_template = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedConnect - Desarrollo Local</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <div class="container">
        <h1>🏥 MedConnect</h1>
        <p><strong>Modo:</strong> Desarrollo Local</p>
        <p><strong>Estado:</strong> <span id="status">Cargando...</span></p>
        
        <div id="user-info" style="display: none;">
            <h2>👤 Información del Usuario</h2>
            <p><strong>ID:</strong> <span id="user-id"></span></p>
            <p><strong>Email:</strong> <span id="user-email"></span></p>
            <p><strong>Tipo:</strong> <span id="user-type"></span></p>
            <a href="/logout" class="btn">Cerrar Sesión</a>
        </div>
        
        <div id="login-section">
            <h2>🔐 Iniciar Sesión</h2>
            <p>Usuarios de prueba disponibles:</p>
            <ul>
                <li><strong>Paciente:</strong> paciente@test.com / password123</li>
                <li><strong>Profesional:</strong> diego.castro.lagos@gmail.com / password123</li>
            </ul>
            <a href="/login" class="btn">Ir al Login</a>
        </div>
        
        <div id="api-tests">
            <h2>🧪 Pruebas de API</h2>
            <button onclick="testHealth()" class="btn">Probar Health Check</button>
            <button onclick="testPatientData()" class="btn">Probar Datos de Paciente</button>
            <div id="api-results"></div>
        </div>
    </div>

    <script>
        // Verificar estado de la aplicación
        fetch('/health')
            .then(response => response.json())
            .then(data => {
                document.getElementById('status').textContent = data.status;
                document.getElementById('status').style.color = data.status === 'healthy' ? 'green' : 'red';
            })
            .catch(error => {
                document.getElementById('status').textContent = 'Error';
                document.getElementById('status').style.color = 'red';
            });

        // Verificar si el usuario está logueado
        fetch('/api/profile/current', { credentials: 'same-origin' })
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('No autenticado');
            })
            .then(data => {
                document.getElementById('user-info').style.display = 'block';
                document.getElementById('login-section').style.display = 'none';
                document.getElementById('user-id').textContent = data.id || 'N/A';
                document.getElementById('user-email').textContent = data.email || 'N/A';
                document.getElementById('user-type').textContent = data.tipo_usuario || 'N/A';
            })
            .catch(error => {
                console.log('Usuario no autenticado');
            });

        function testHealth() {
            fetch('/health')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('api-results').innerHTML = 
                        '<div class="alert alert-success"><pre>' + JSON.stringify(data, null, 2) + '</pre></div>';
                })
                .catch(error => {
                    document.getElementById('api-results').innerHTML = 
                        '<div class="alert alert-error">Error: ' + error.message + '</div>';
                });
        }

        function testPatientData() {
            fetch('/api/patient/1/consultations')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('api-results').innerHTML = 
                        '<div class="alert alert-success"><pre>Consultas: ' + JSON.stringify(data, null, 2) + '</pre></div>';
                })
                .catch(error => {
                    document.getElementById('api-results').innerHTML = 
                        '<div class="alert alert-error">Error: ' + error.message + '</div>';
                });
        }
    </script>
</body>
</html>"""
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(basic_template)
        print(f"  ✅ Template básico creado: {template_file}")
    
    print("\n✅ Entorno de desarrollo configurado")
    print("📝 Próximos pasos:")
    print("   1. Ejecuta: python run_local.py")
    print("   2. Abre: http://localhost:5000")
    print("   3. Prueba las funcionalidades")

if __name__ == "__main__":
    setup_dev_environment() 