#!/usr/bin/env python3
"""
Script para limpiar caché del navegador y forzar recarga de estilos CSS
"""

import os
import time
import webbrowser
from datetime import datetime

def limpiar_cache_y_forzar_recarga():
    """Limpia caché y fuerza recarga de estilos"""
    
    print("🔄 LIMPIANDO CACHÉ Y FORZANDO RECARGA DE ESTILOS")
    print("=" * 60)
    
    # 1. Verificar que el archivo CSS existe
    css_file = "static/css/professional-styles.css"
    if not os.path.exists(css_file):
        print(f"❌ Error: No se encuentra el archivo {css_file}")
        return False
    
    print(f"✅ Archivo CSS encontrado: {css_file}")
    
    # 2. Actualizar timestamp en el archivo CSS
    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar y actualizar el comentario de timestamp
        if "/* Professional Dashboard Styles" in content:
            new_timestamp = f"/* Professional Dashboard Styles - Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} */"
            content = content.replace("/* Professional Dashboard Styles - Updated:", new_timestamp)
            
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Timestamp actualizado en CSS")
        else:
            print("⚠️ No se encontró el comentario de timestamp")
            
    except Exception as e:
        print(f"❌ Error actualizando CSS: {e}")
        return False
    
    # 3. Instrucciones para el usuario
    print("\n📋 INSTRUCCIONES PARA FORZAR RECARGA:")
    print("=" * 60)
    
    print("1. 🔄 Recarga forzada del navegador:")
    print("   • Windows/Linux: Ctrl + F5 o Ctrl + Shift + R")
    print("   • Mac: Cmd + Shift + R")
    print("   • O presiona F12 → Network → Disable cache")
    
    print("\n2. 🧹 Limpiar caché del navegador:")
    print("   • Chrome: Ctrl + Shift + Delete")
    print("   • Firefox: Ctrl + Shift + Delete")
    print("   • Safari: Cmd + Option + E")
    
    print("\n3. 🔍 Verificar cambios:")
    print("   • Abre las herramientas de desarrollador (F12)")
    print("   • Ve a la pestaña 'Network'")
    print("   • Marca 'Disable cache'")
    print("   • Recarga la página")
    
    print("\n4. 🎨 Verificar estilos:")
    print("   • Busca las clases: .dashboard-header, .stat-card-mini")
    print("   • Verifica que aparezcan los detalles morados")
    print("   • Comprueba los colores de las tarjetas")
    
    # 4. Crear archivo de verificación
    verification_file = "verificacion_estilos.html"
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verificación de Estilos - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <link rel="stylesheet" href="static/css/professional-styles.css?v={int(time.time())}">
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .test-container {{ max-width: 800px; margin: 0 auto; }}
        .test-section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
        .test-title {{ color: #6f42c1; font-weight: bold; margin-bottom: 10px; }}
        .test-description {{ color: #666; margin-bottom: 15px; }}
        .dashboard-header {{ background: linear-gradient(135deg, #6f42c1 0%, #8e44ad 100%); color: white; padding: 20px; border-radius: 8px; margin: 10px 0; }}
        .stat-card-mini {{ background: rgba(255, 255, 255, 0.15); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px; padding: 15px; margin: 10px; text-align: center; position: relative; }}
        .stat-card-mini.atenciones {{ --card-accent-color: #28a745; }}
        .stat-card-mini.citas-hoy {{ --card-accent-color: #17a2b8; }}
        .stat-card-mini.pacientes {{ --card-accent-color: #ffc107; }}
        .stat-card-mini.pendientes {{ --card-accent-color: #dc3545; }}
    </style>
</head>
<body>
    <div class="test-container">
        <h1>🎨 Verificación de Estilos CSS</h1>
        <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="test-section">
            <div class="test-title">✅ Dashboard Header con Detalles Morados</div>
            <div class="test-description">Debe mostrar shimmer superior y círculo pulsante</div>
            <div class="dashboard-header">
                <h1>¡Hola, Giselle!</h1>
                <p>Giselle Arratia</p>
                <p>Sistema de Gestión de Atenciones Médicas</p>
                <small>Último acceso: 2025-07-31</small>
            </div>
        </div>
        
        <div class="test-section">
            <div class="test-title">✅ Tarjetas con Colores Característicos</div>
            <div class="test-description">Cada tarjeta debe tener su color específico y detalle morado</div>
            <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                <div class="stat-card-mini atenciones">
                    <div style="font-size: 2rem; margin-bottom: 5px;">📋</div>
                    <div style="font-size: 1.5rem; font-weight: bold;">2</div>
                    <small>Atenciones</small>
                </div>
                <div class="stat-card-mini citas-hoy">
                    <div style="font-size: 2rem; margin-bottom: 5px;">📅</div>
                    <div style="font-size: 1.5rem; font-weight: bold;">0</div>
                    <small>Citas Hoy</small>
                </div>
                <div class="stat-card-mini pacientes">
                    <div style="font-size: 2rem; margin-bottom: 5px;">👥</div>
                    <div style="font-size: 1.5rem; font-weight: bold;">4</div>
                    <small>Pacientes</small>
                </div>
                <div class="stat-card-mini pendientes">
                    <div style="font-size: 2rem; margin-bottom: 5px;">⏰</div>
                    <div style="font-size: 1.5rem; font-weight: bold;">0</div>
                    <small>Pendientes</small>
                </div>
            </div>
        </div>
        
        <div class="test-section">
            <div class="test-title">📋 Lista de Verificación</div>
            <div class="test-description">Marque los elementos que puede ver:</div>
            <ul>
                <li>☐ Shimmer superior en el header (barra animada)</li>
                <li>☐ Círculo pulsante en la esquina derecha del header</li>
                <li>☐ Punto flotante en la sección de bienvenida</li>
                <li>☐ Barra lateral morada en estadísticas</li>
                <li>☐ Punto parpadeante en estadísticas</li>
                <li>☐ Punto decorativo junto al título</li>
                <li>☐ Punto en el primer párrafo</li>
                <li>☐ Detalles morados en las esquinas de las tarjetas</li>
                <li>☐ Colores específicos para cada tarjeta (verde, azul, amarillo, rojo)</li>
                <li>☐ Efectos hover en las tarjetas</li>
            </ul>
        </div>
        
        <div class="test-section">
            <div class="test-title">🔧 Solución de Problemas</div>
            <div class="test-description">Si no ve los cambios:</div>
            <ol>
                <li>Presione Ctrl + F5 (Windows/Linux) o Cmd + Shift + R (Mac)</li>
                <li>Abra F12 → Network → Marque "Disable cache"</li>
                <li>Recargue la página</li>
                <li>Verifique que el archivo CSS se está cargando correctamente</li>
                <li>Compruebe que no hay errores en la consola del navegador</li>
            </ol>
        </div>
    </div>
</body>
</html>
"""
    
    try:
        with open(verification_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Archivo de verificación creado: {verification_file}")
    except Exception as e:
        print(f"❌ Error creando archivo de verificación: {e}")
    
    print("\n✅ PROCESO COMPLETADO")
    print("=" * 60)
    print("📝 Siguiente paso: Recarga forzada del navegador")
    print("🎯 Objetivo: Ver los detalles morados y colores de tarjetas")
    
    return True

if __name__ == "__main__":
    limpiar_cache_y_forzar_recarga() 