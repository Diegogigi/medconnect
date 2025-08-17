#!/usr/bin/env python3
"""
Script para forzar la recarga del CSS en la aplicación Flask
"""

import os
import time
from datetime import datetime

def forzar_recarga_css():
    """Fuerza la recarga del CSS agregando parámetros de versión"""
    
    print("🔄 FORZANDO RECARGA DE CSS EN LA APLICACIÓN")
    print("=" * 60)
    
    # 1. Verificar archivos CSS
    css_files = [
        "static/css/professional-styles.css",
        "static/css/styles.css",
        "static/css/patient-styles.css"
    ]
    
    for css_file in css_files:
        if os.path.exists(css_file):
            print(f"✅ Encontrado: {css_file}")
        else:
            print(f"⚠️ No encontrado: {css_file}")
    
    # 2. Actualizar timestamp en todos los archivos CSS
    timestamp = int(time.time())
    
    for css_file in css_files:
        if os.path.exists(css_file):
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar y actualizar comentario de timestamp
                if "/* Professional Dashboard Styles" in content:
                    new_timestamp = f"/* Professional Dashboard Styles - Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - v{timestamp} */"
                    content = content.replace("/* Professional Dashboard Styles - Updated:", new_timestamp)
                    
                    with open(css_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"✅ Actualizado timestamp en: {css_file}")
                
            except Exception as e:
                print(f"❌ Error actualizando {css_file}: {e}")
    
    # 3. Crear archivo de configuración para Flask
    flask_config = f"""
# Configuración para forzar recarga de CSS
# Agregar a app.py o config.py

import time

# Versión del CSS para evitar caché
CSS_VERSION = {timestamp}

# Función para generar URLs de CSS con versión
def css_url(filename):
    return f'/static/css/{{filename}}?v={{CSS_VERSION}}'

# En las plantillas, usar:
# <link rel="stylesheet" href="{{ css_url('professional-styles.css') }}">
"""
    
    try:
        with open("css_version_config.py", 'w', encoding='utf-8') as f:
            f.write(flask_config)
        print("✅ Archivo de configuración CSS creado: css_version_config.py")
    except Exception as e:
        print(f"❌ Error creando configuración: {e}")
    
    # 4. Instrucciones para el usuario
    print("\n📋 INSTRUCCIONES PARA APLICAR CAMBIOS:")
    print("=" * 60)
    
    print("1. 🔄 Recarga forzada del navegador:")
    print("   • Windows/Linux: Ctrl + F5 o Ctrl + Shift + R")
    print("   • Mac: Cmd + Shift + R")
    print("   • O presiona F12 → Network → Disable cache")
    
    print("\n2. 🧹 Limpiar caché del navegador:")
    print("   • Chrome: Ctrl + Shift + Delete")
    print("   • Firefox: Ctrl + Shift + Delete")
    print("   • Safari: Cmd + Option + E")
    
    print("\n3. 🔍 Verificar en la aplicación:")
    print("   • Abre la aplicación Flask")
    print("   • Ve al dashboard profesional")
    print("   • Verifica los detalles morados y colores")
    
    print("\n4. 🎨 Elementos a verificar:")
    print("   • Shimmer superior en el header")
    print("   • Círculo pulsante en la esquina derecha")
    print("   • Punto flotante en la sección de bienvenida")
    print("   • Barra lateral morada en estadísticas")
    print("   • Punto parpadeante en estadísticas")
    print("   • Detalles morados en las tarjetas")
    print("   • Colores específicos para cada tarjeta")
    
    print("\n5. 🔧 Si aún no se ven los cambios:")
    print("   • Reinicia el servidor Flask")
    print("   • Limpia completamente el caché del navegador")
    print("   • Usa modo incógnito/privado")
    print("   • Verifica que no hay errores en la consola")
    
    # 5. Crear archivo de verificación rápida
    quick_check = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verificación Rápida CSS - v{timestamp}</title>
    <link rel="stylesheet" href="static/css/professional-styles.css?v={timestamp}">
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        .status {{ padding: 10px; margin: 10px 0; border-radius: 4px; }}
        .success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }}
        .test-element {{ 
            background: linear-gradient(135deg, #6f42c1 0%, #8e44ad 100%); 
            color: white; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 10px 0;
            position: relative;
            overflow: hidden;
        }}
        .test-element::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, #6f42c1, #8e44ad, #6f42c1);
            background-size: 200% 100%;
            animation: shimmer 3s ease-in-out infinite;
        }}
        @keyframes shimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
        .stat-card {{
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 15px;
            margin: 10px;
            text-align: center;
            position: relative;
            display: inline-block;
            width: 120px;
        }}
        .stat-card.atenciones {{ --card-accent-color: #28a745; }}
        .stat-card.citas-hoy {{ --card-accent-color: #17a2b8; }}
        .stat-card.pacientes {{ --card-accent-color: #ffc107; }}
        .stat-card.pendientes {{ --card-accent-color: #dc3545; }}
        .stat-card::after {{
            content: '';
            position: absolute;
            bottom: 5px;
            right: 5px;
            width: 6px;
            height: 6px;
            background: linear-gradient(45deg, #6f42c1, #8e44ad);
            border-radius: 50%;
            opacity: 0.6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Verificación Rápida CSS</h1>
        <p><strong>Versión:</strong> v{timestamp}</p>
        <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="status success">
            ✅ Si ves el header morado con shimmer, el CSS está funcionando
        </div>
        
        <div class="test-element">
            <h2>Dashboard Header</h2>
            <p>Debe mostrar shimmer superior y gradiente morado</p>
        </div>
        
        <div style="text-align: center;">
            <div class="stat-card atenciones">
                <div style="font-size: 1.5rem;">📋</div>
                <div style="font-weight: bold;">2</div>
                <small>Atenciones</small>
            </div>
            <div class="stat-card citas-hoy">
                <div style="font-size: 1.5rem;">📅</div>
                <div style="font-weight: bold;">0</div>
                <small>Citas Hoy</small>
            </div>
            <div class="stat-card pacientes">
                <div style="font-size: 1.5rem;">👥</div>
                <div style="font-weight: bold;">4</div>
                <small>Pacientes</small>
            </div>
            <div class="stat-card pendientes">
                <div style="font-size: 1.5rem;">⏰</div>
                <div style="font-weight: bold;">0</div>
                <small>Pendientes</small>
            </div>
        </div>
        
        <div class="status warning">
            ⚠️ Si no ves los efectos, recarga con Ctrl+F5
        </div>
    </div>
</body>
</html>
"""
    
    try:
        with open("verificacion_rapida.html", 'w', encoding='utf-8') as f:
            f.write(quick_check)
        print("✅ Archivo de verificación rápida creado: verificacion_rapida.html")
    except Exception as e:
        print(f"❌ Error creando verificación rápida: {e}")
    
    print(f"\n✅ PROCESO COMPLETADO - Versión CSS: v{timestamp}")
    print("=" * 60)
    print("🎯 Próximo paso: Recarga forzada del navegador")
    
    return timestamp

if __name__ == "__main__":
    forzar_recarga_css() 