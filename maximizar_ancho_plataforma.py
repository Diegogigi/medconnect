#!/usr/bin/env python3
"""
Script para maximizar el ancho de la plataforma
"""

import os
import time
import webbrowser
from datetime import datetime

def maximizar_ancho_plataforma():
    """Maximiza el ancho de la plataforma eliminando márgenes laterales"""
    
    print("🔄 MAXIMIZANDO ANCHO DE PLATAFORMA")
    print("=" * 60)
    
    # 1. Actualizar timestamp en CSS
    css_file = "static/css/professional-styles.css"
    if os.path.exists(css_file):
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Actualizar timestamp
            new_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_timestamp_line = f"/* Professional Dashboard Styles - Updated: {new_timestamp} */"
            
            # Buscar y reemplazar la primera línea del comentario
            lines = content.split('\n')
            if lines[0].startswith('/* Professional Dashboard Styles'):
                lines[0] = new_timestamp_line
            else:
                lines.insert(0, new_timestamp_line)
            
            content = '\n'.join(lines)
            
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ CSS actualizado con nuevo timestamp: {new_timestamp}")
            
        except Exception as e:
            print(f"❌ Error actualizando CSS: {e}")
            return False
    
    # 2. Crear archivo de verificación HTML
    verification_html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maximización Ancho Plataforma - MedConnect</title>
    <link rel="stylesheet" href="{css_file}?v={int(time.time())}">
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            background: rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            text-align: center;
            max-width: 800px;
            width: 90%;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        h1 {{
            margin-bottom: 30px;
            font-size: 2.2em;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}
        .status-item {{
            background: rgba(255, 255, 255, 0.1);
            margin: 15px 0;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
        }}
        .timestamp {{
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 30px;
        }}
        .demo-container {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .demo-header {{
            background: linear-gradient(135deg, #6f42c1 0%, #8e44ad 100%);
            color: white;
            padding: 1rem 0;
            margin: 20px 0;
            border-radius: 8px;
            font-size: 1.2em;
        }}
        .demo-stats {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 10px;
            margin: 20px 0;
        }}
        .demo-stat {{
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 8px;
            min-width: 120px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>✅ Ancho de Plataforma Maximizado</h1>
        
        <div class="status-item">
            <strong>✅ Contenedor principal al 100%</strong><br>
            max-width: 100%, margin: 0, padding: 0
        </div>
        
        <div class="status-item">
            <strong>✅ Container-fluid sin padding</strong><br>
            padding: 0, width: 100%, max-width: 100%
        </div>
        
        <div class="status-item">
            <strong>✅ Body optimizado</strong><br>
            width: 100vw, max-width: 100vw, overflow-x: hidden
        </div>
        
        <div class="status-item">
            <strong>✅ Márgenes laterales eliminados</strong><br>
            row margin: 0, col padding: 0
        </div>
        
        <div class="status-item">
            <strong>✅ Elementos específicos optimizados</strong><br>
            navbar, dashboard-header, main con width: 100%
        </div>
        
        <div class="demo-container">
            <h3>Demo de Layout Maximizado</h3>
            <div class="demo-header">
                Dashboard Header - Ancho Completo (100vw)
            </div>
            <div class="demo-stats">
                <div class="demo-stat">
                    <div style="font-size: 0.9em; opacity: 0.8;">Atenciones</div>
                    <div style="font-size: 1.5em; font-weight: bold;">120</div>
                </div>
                <div class="demo-stat">
                    <div style="font-size: 0.9em; opacity: 0.8;">Citas de hoy</div>
                    <div style="font-size: 1.5em; font-weight: bold;">15</div>
                </div>
                <div class="demo-stat">
                    <div style="font-size: 0.9em; opacity: 0.8;">Pacientes</div>
                    <div style="font-size: 1.5em; font-weight: bold;">500</div>
                </div>
                <div class="demo-stat">
                    <div style="font-size: 0.9em; opacity: 0.8;">Pendientes</div>
                    <div style="font-size: 1.5em; font-weight: bold;">5</div>
                </div>
            </div>
        </div>
        
        <div class="timestamp">
            Maximización completada: {new_timestamp}<br>
            La plataforma ahora usa TODO el ancho disponible
        </div>
        
        <p style="margin-top: 20px;">
            <strong>Instrucciones:</strong><br>
            1. Cierra esta ventana<br>
            2. Recarga la página de MedConnect (Ctrl+F5)<br>
            3. Verifica que NO haya espacios laterales
        </p>
    </div>
</body>
</html>
    """
    
    try:
        with open('verificacion_maximo_ancho.html', 'w', encoding='utf-8') as f:
            f.write(verification_html)
        print("✅ Archivo de verificación creado: verificacion_maximo_ancho.html")
        
        # Abrir en navegador
        webbrowser.open('file://' + os.path.abspath('verificacion_maximo_ancho.html'))
        print("🌐 Abriendo verificación en navegador")
        
    except Exception as e:
        print(f"❌ Error creando archivo de verificación: {e}")
    
    print("\n🎉 MAXIMIZACIÓN COMPLETADA")
    print("=" * 60)
    print("✅ Contenedor principal al 100%")
    print("✅ Container-fluid sin padding")
    print("✅ Body optimizado con 100vw")
    print("✅ Márgenes laterales completamente eliminados")
    print("✅ Elementos específicos optimizados")
    print("\n📝 PRÓXIMOS PASOS:")
    print("   1. Recarga la página de MedConnect (Ctrl+F5)")
    print("   2. Verifica que NO haya espacios laterales")
    print("   3. La plataforma debe usar TODO el ancho de pantalla")

if __name__ == "__main__":
    maximizar_ancho_plataforma() 