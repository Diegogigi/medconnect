#!/usr/bin/env python3
"""
Configuración específica para archivos estáticos en Railway
Este archivo se puede importar en app.py para mejorar el manejo de archivos estáticos
"""

import os
import shutil
from pathlib import Path

def setup_railway_static_files():
    """
    Configura los archivos estáticos para Railway
    Asegura que todos los archivos necesarios estén en las ubicaciones correctas
    """
    print("🔧 Configurando archivos estáticos para Railway...")
    
    # Rutas base
    current_dir = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Rutas de static a verificar
    static_paths = [
        os.path.join(script_dir, 'static'),
        os.path.join(current_dir, 'static'),
        'static'
    ]
    
    # Encontrar la carpeta static principal
    main_static_path = None
    for static_path in static_paths:
        if os.path.exists(static_path) and os.path.isdir(static_path):
            main_static_path = static_path
            break
    
    if not main_static_path:
        print("❌ No se encontró carpeta static principal")
        return False
    
    print(f"✅ Carpeta static principal encontrada: {main_static_path}")
    
    # Verificar y crear subcarpetas necesarias
    subdirs = ['css', 'js', 'images', 'uploads']
    for subdir in subdirs:
        subdir_path = os.path.join(main_static_path, subdir)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path, exist_ok=True)
            print(f"✅ Creada subcarpeta: {subdir}")
    
    # Verificar archivos críticos
    critical_files = {
        'css/styles.css': 'Archivo CSS principal',
        'js/app.js': 'Archivo JavaScript principal',
        'images/logo.png': 'Logo de la aplicación',
        'images/Imagen2.png': 'Imagen secundaria'
    }
    
    missing_files = []
    for file_path, description in critical_files.items():
        full_path = os.path.join(main_static_path, file_path)
        if not os.path.exists(full_path):
            missing_files.append((file_path, description))
            print(f"⚠️ Archivo faltante: {file_path} ({description})")
        else:
            print(f"✅ Archivo encontrado: {file_path}")
    
    if missing_files:
        print(f"\n⚠️ Archivos faltantes: {len(missing_files)}")
        print("Esto puede causar errores 404 en Railway")
        return False
    
    print("✅ Todos los archivos críticos están presentes")
    return True

def get_static_file_path(filename):
    """
    Obtiene la ruta completa de un archivo estático
    Busca en múltiples ubicaciones para compatibilidad con Railway
    """
    static_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'),
        os.path.join(os.getcwd(), 'static'),
        'static'
    ]
    
    for static_path in static_paths:
        file_path = os.path.join(static_path, filename)
        if os.path.exists(file_path):
            return file_path
    
    return None

def verify_static_file(filename):
    """
    Verifica si un archivo estático existe y es accesible
    """
    file_path = get_static_file_path(filename)
    if not file_path:
        return False, None
    
    try:
        # Verificar que el archivo existe y es legible
        if os.path.exists(file_path) and os.access(file_path, os.R_OK):
            size = os.path.getsize(file_path)
            return True, {
                'path': file_path,
                'size': size,
                'readable': True
            }
        else:
            return False, None
    except Exception:
        return False, None

if __name__ == "__main__":
    setup_railway_static_files() 