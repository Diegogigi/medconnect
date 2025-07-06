#!/usr/bin/env python3
"""
Script de diagnóstico para archivos estáticos en Railway
Ejecutar este script para verificar el estado de los archivos estáticos
"""

import os
import sys
import json
from pathlib import Path

def check_static_files():
    """Verifica el estado de los archivos estáticos"""
    print("🔍 === DIAGNÓSTICO DE ARCHIVOS ESTÁTICOS EN RAILWAY ===")
    print()
    
    # Obtener rutas del proyecto
    current_dir = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"📂 Directorio actual: {current_dir}")
    print(f"📂 Directorio del script: {script_dir}")
    print()
    
    # Rutas a verificar
    static_paths = [
        os.path.join(script_dir, 'static'),
        os.path.join(current_dir, 'static'),
        'static'
    ]
    
    print("🔍 === VERIFICANDO CARPETAS STATIC ===")
    for i, static_path in enumerate(static_paths):
        exists = os.path.exists(static_path)
        is_dir = os.path.isdir(static_path) if exists else False
        print(f"  {i+1}. {static_path}")
        print(f"     Existe: {'✅' if exists else '❌'}")
        print(f"     Es directorio: {'✅' if is_dir else '❌'}")
        if exists and is_dir:
            try:
                files = os.listdir(static_path)
                print(f"     Archivos encontrados: {len(files)}")
                if files:
                    print(f"     Primeros archivos: {files[:5]}")
            except Exception as e:
                print(f"     Error listando archivos: {e}")
        print()
    
    # Verificar archivos críticos
    critical_files = [
        'css/styles.css',
        'js/app.js',
        'images/logo.png',
        'images/Imagen2.png'
    ]
    
    print("🔍 === VERIFICANDO ARCHIVOS CRÍTICOS ===")
    for file_rel_path in critical_files:
        print(f"\n📄 {file_rel_path}:")
        
        found = False
        for static_path in static_paths:
            file_path = os.path.join(static_path, file_rel_path)
            exists = os.path.exists(file_path)
            
            if exists:
                try:
                    size = os.path.getsize(file_path)
                    readable = os.access(file_path, os.R_OK)
                    print(f"  ✅ Encontrado en: {static_path}")
                    print(f"     Tamaño: {size} bytes")
                    print(f"     Legible: {'✅' if readable else '❌'}")
                    found = True
                    break
                except Exception as e:
                    print(f"  ⚠️ Error accediendo: {e}")
            else:
                print(f"  ❌ No encontrado en: {static_path}")
        
        if not found:
            print(f"  ❌ ARCHIVO NO ENCONTRADO EN NINGUNA UBICACIÓN")
    
    print("\n🔍 === VERIFICANDO PERMISOS ===")
    for static_path in static_paths:
        if os.path.exists(static_path):
            try:
                # Verificar permisos de la carpeta
                readable = os.access(static_path, os.R_OK)
                writable = os.access(static_path, os.W_OK)
                executable = os.access(static_path, os.X_OK)
                
                print(f"\n📁 Permisos de {static_path}:")
                print(f"  Lectura: {'✅' if readable else '❌'}")
                print(f"  Escritura: {'✅' if writable else '❌'}")
                print(f"  Ejecución: {'✅' if executable else '❌'}")
                
                # Verificar permisos de archivos dentro
                try:
                    files = os.listdir(static_path)
                    for file in files[:3]:  # Solo los primeros 3
                        file_path = os.path.join(static_path, file)
                        if os.path.isfile(file_path):
                            file_readable = os.access(file_path, os.R_OK)
                            print(f"  📄 {file}: {'✅' if file_readable else '❌'}")
                except Exception as e:
                    print(f"  Error verificando archivos: {e}")
                    
            except Exception as e:
                print(f"  Error verificando permisos: {e}")
    
    print("\n🔍 === INFORMACIÓN DEL SISTEMA ===")
    print(f"  Sistema operativo: {sys.platform}")
    print(f"  Versión de Python: {sys.version}")
    print(f"  Variables de entorno:")
    env_vars = ['RAILWAY_ENVIRONMENT', 'PORT', 'FLASK_ENV', 'PYTHON_VERSION']
    for var in env_vars:
        value = os.environ.get(var, 'No definida')
        print(f"    {var}: {value}")
    
    print("\n✅ === DIAGNÓSTICO COMPLETADO ===")

if __name__ == "__main__":
    check_static_files() 