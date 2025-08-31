#!/usr/bin/env python3
"""
Script para crear una función index simple que funcione
"""


def fix_index_simple():
    """Crea una función index simple que funcione"""

    print("🔧 Creando función index simple...")

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar la función index
    old_index = '''@app.route("/")
def index():
    """Página principal - Landing page original"""
    return render_template("index.html")'''

    new_index = '''@app.route("/")
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

    # Reemplazar en el contenido
    if old_index in content:
        content = content.replace(old_index, new_index)

        # Escribir el archivo actualizado
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Función index simplificada creada")
        print("🔧 Incluye fallback si el template falla")
    else:
        print("❌ No se encontró la función index actual")


if __name__ == "__main__":
    fix_index_simple()
