#!/usr/bin/env python3
"""
Script para arreglar el dashboard de pacientes
"""


def fix_patient_dashboard():
    """Arregla el dashboard de pacientes"""

    print("🔧 Arreglando dashboard de pacientes...")

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar la función patient_dashboard
    old_patient_dashboard = """@app.route("/patient")
@login_required
def patient_dashboard():
    return (
        render_template("patient_dashboard.html")
        if os.path.exists(os.path.join("templates", "patient_dashboard.html"))
        else "Paciente"
    )"""

    new_patient_dashboard = '''@app.route("/patient")
@login_required
def patient_dashboard():
    """Dashboard del paciente con datos del usuario"""
    try:
        # Obtener datos del usuario desde la sesión
        user_id = session.get("user_id")
        user_email = session.get("user_email")
        user_name = session.get("user_name")
        user_type = session.get("user_type", "paciente")
        
        # Crear objeto user para el template
        user = {
            "id": user_id,
            "email": user_email,
            "nombre": user_name,
            "tipo_usuario": user_type
        }
        
        # Intentar usar el template patient.html
        return render_template("patient.html", user=user, just_logged_in=False)
    except Exception as e:
        logger.error(f"❌ Error cargando patient.html: {e}")
        # Fallback a página simple
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MedConnect - Dashboard Paciente</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background: #f5f5f5; 
                }}
                .container {{ 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 10px; 
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); 
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 30px; 
                    padding-bottom: 20px; 
                    border-bottom: 2px solid #007bff; 
                }}
                .user-info {{ 
                    background: #f8f9fa; 
                    padding: 20px; 
                    border-radius: 8px; 
                    margin-bottom: 30px; 
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
                .btn:hover {{ 
                    background: #0056b3; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 MedConnect</h1>
                    <h2>Dashboard del Paciente</h2>
                </div>
                
                <div class="user-info">
                    <h3>👤 Información del Usuario</h3>
                    <p><strong>ID:</strong> {user_id}</p>
                    <p><strong>Email:</strong> {user_email}</p>
                    <p><strong>Nombre:</strong> {user_name}</p>
                    <p><strong>Tipo:</strong> {user_type}</p>
                </div>
                
                <div style="text-align: center;">
                    <h3>🚧 Dashboard en Desarrollo</h3>
                    <p>El dashboard completo estará disponible pronto.</p>
                    
                    <a href="/" class="btn">← Volver al Inicio</a>
                    <a href="/logout" class="btn">Cerrar Sesión</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html'''

    # Reemplazar en el contenido
    if old_patient_dashboard in content:
        content = content.replace(old_patient_dashboard, new_patient_dashboard)

        # Escribir el archivo actualizado
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Dashboard de pacientes arreglado")
        print("🔧 Incluye datos del usuario y fallback robusto")
    else:
        print("❌ No se encontró la función patient_dashboard actual")


if __name__ == "__main__":
    fix_patient_dashboard()
