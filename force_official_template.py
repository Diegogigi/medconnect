#!/usr/bin/env python3
"""
Script para forzar el uso del template oficial y mostrar errores específicos
"""


def force_official_template():
    """Fuerza el uso del template oficial y muestra errores específicos"""

    print("🔧 Forzando uso del template oficial...")

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar la función index
    old_index = '''@app.route("/")
def index():
    """Página principal - Landing page simple"""
    try:
        # Intentar usar el template original
        return render_template("index.html")
    except Exception as e:
        logger.error(f"❌ Error cargando template index.html: {e}")
        # Fallback a página simple
        html = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MedConnect - Gestión Médica Familiar</title>
            <style>
                body { 
                    font-family: 'Inter', Arial, sans-serif; 
                    margin: 0; 
                    padding: 0; 
                    background: linear-gradient(135deg, #0066cc 0%, #6366f1 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .container { 
                    background: white; 
                    padding: 40px; 
                    border-radius: 16px; 
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    text-align: center;
                    max-width: 500px;
                    width: 90%;
                }
                h1 { 
                    color: #0066cc; 
                    margin-bottom: 20px;
                    font-size: 2.5em;
                }
                p { 
                    color: #6b7280; 
                    margin-bottom: 30px;
                    line-height: 1.6;
                }
                .btn { 
                    background: linear-gradient(135deg, #0066cc 0%, #6366f1 100%);
                    color: white; 
                    padding: 15px 30px; 
                    text-decoration: none; 
                    border-radius: 8px; 
                    display: inline-block; 
                    margin: 10px;
                    font-weight: 600;
                    transition: transform 0.2s;
                }
                .btn:hover { 
                    transform: translateY(-2px);
                }
                .features {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }
                .feature {
                    padding: 20px;
                    background: #f8fafc;
                    border-radius: 8px;
                    border-left: 4px solid #0066cc;
                }
                .feature h3 {
                    color: #0066cc;
                    margin-bottom: 10px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏥 MedConnect</h1>
                <p>Sistema integral de gestión médica familiar con Asistente de IA inteligente</p>
                
                <div class="features">
                    <div class="feature">
                        <h3>📅 Gestión de Citas</h3>
                        <p>Organiza y gestiona citas médicas familiares</p>
                    </div>
                    <div class="feature">
                        <h3>💊 Control de Medicamentos</h3>
                        <p>Monitorea tratamientos y medicamentos</p>
                    </div>
                    <div class="feature">
                        <h3>🤖 IA Asistente</h3>
                        <p>Asistente inteligente para consultas médicas</p>
                    </div>
                </div>
                
                <a href="/login" class="btn">Iniciar Sesión</a>
                <a href="/health" class="btn">Estado del Sistema</a>
            </div>
        </body>
        </html>
        """
        return html'''

    new_index = '''@app.route("/")
def index():
    """Página principal - Template oficial"""
    try:
        # Verificar que el template existe
        template_path = os.path.join("templates", "index.html")
        if not os.path.exists(template_path):
            logger.error(f"❌ Template no encontrado: {template_path}")
            raise FileNotFoundError(f"Template no encontrado: {template_path}")
        
        logger.info("✅ Template index.html encontrado, renderizando...")
        return render_template("index.html")
        
    except Exception as e:
        logger.error(f"❌ Error cargando template index.html: {e}")
        logger.error(f"❌ Tipo de error: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback completo: {traceback.format_exc()}")
        
        # Fallback temporal con información del error
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MedConnect - Error de Template</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background: #f5f5f5; 
                }}
                .container {{ 
                    max-width: 800px; 
                    margin: 50px auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 10px; 
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); 
                }}
                .error {{ 
                    background: #f8d7da; 
                    color: #721c24; 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin: 20px 0; 
                }}
                .btn {{ 
                    background: #007bff; 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 4px; 
                    display: inline-block; 
                    margin: 10px 5px; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏥 MedConnect</h1>
                <h2>Error al cargar template oficial</h2>
                
                <div class="error">
                    <h3>Error detectado:</h3>
                    <p><strong>Tipo:</strong> {type(e).__name__}</p>
                    <p><strong>Mensaje:</strong> {str(e)}</p>
                </div>
                
                <p>El template oficial no se pudo cargar. Esto puede ser por:</p>
                <ul>
                    <li>Archivo estático faltante</li>
                    <li>Error de sintaxis en el template</li>
                    <li>Variable Jinja2 no definida</li>
                </ul>
                
                <a href="/login" class="btn">Ir al Login</a>
                <a href="/health" class="btn">Estado del Sistema</a>
            </div>
        </body>
        </html>
        """
        return html'''

    # Reemplazar en el contenido
    if old_index in content:
        content = content.replace(old_index, new_index)

        # Escribir el archivo actualizado
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Función index actualizada para forzar template oficial")
        print("🔧 Ahora mostrará errores específicos si falla")
    else:
        print("❌ No se encontró la función index actual")


if __name__ == "__main__":
    force_official_template()
