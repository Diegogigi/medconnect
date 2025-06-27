#!/usr/bin/env python3
"""
Script de diagnóstico para verificar archivos estáticos
"""

import os
import sys

def check_static_files():
    """Verifica que los archivos estáticos existan"""
    print("🔍 Verificando archivos estáticos...")
    
    # Directorio static
    static_dir = 'static'
    if not os.path.exists(static_dir):
        print(f"❌ Directorio {static_dir} no existe")
        return False
    
    print(f"✅ Directorio {static_dir} existe")
    
    # Archivos críticos
    critical_files = [
        'static/css/styles.css',
        'static/js/app.js',
        'static/images/logo.png'
    ]
    
    all_good = True
    for file_path in critical_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_path} - {file_size} bytes")
        else:
            print(f"❌ {file_path} - NO EXISTE")
            all_good = False
    
    # Listar contenido del directorio static
    print("\n📁 Contenido del directorio static:")
    for root, dirs, files in os.walk(static_dir):
        level = root.replace(static_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            print(f"{subindent}{file} ({file_size} bytes)")
    
    return all_good

def check_flask_config():
    """Verifica la configuración de Flask"""
    print("\n🔧 Verificando configuración de Flask...")
    
    try:
        from app import app
        
        # Verificar configuración
        print(f"✅ Flask app creada")
        print(f"📁 App root path: {app.root_path}")
        print(f"📁 Static folder: {app.static_folder}")
        print(f"🌐 Static url path: {app.static_url_path}")
        
        # Verificar URLs
        with app.test_client() as client:
            # Probar URL de CSS
            response = client.get('/static/css/styles.css')
            print(f"🎨 CSS response: {response.status_code}")
            
            # Probar URL de JS
            response = client.get('/static/js/app.js')
            print(f"📜 JS response: {response.status_code}")
            
            # Probar URL de imagen
            response = client.get('/static/images/logo.png')
            print(f"🖼️ Image response: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando Flask: {e}")
        return False

def main():
    """Función principal"""
    print("🏥 MedConnect - Diagnóstico de archivos estáticos")
    print("=" * 50)
    
    # Verificar archivos estáticos
    files_ok = check_static_files()
    
    # Verificar configuración de Flask
    flask_ok = check_flask_config()
    
    print("\n" + "=" * 50)
    if files_ok and flask_ok:
        print("✅ Todos los archivos estáticos están OK")
        sys.exit(0)
    else:
        print("❌ Hay problemas con los archivos estáticos")
        sys.exit(1)

if __name__ == "__main__":
    main() 