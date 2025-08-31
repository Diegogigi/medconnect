#!/usr/bin/env python3
"""
Script para mejorar el manejo de errores
"""

def improve_error_handling():
    """Mejora el manejo de errores"""
    
    print("🔧 Mejorando manejo de errores...")
    
    # Leer el archivo app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Agregar import de traceback si no existe
    if 'import traceback' not in content:
        # Buscar después de los imports existentes
        imports_end = content.find('from flask import (')
        if imports_end != -1:
            # Encontrar el final de los imports
            end_pos = content.find(')', imports_end) + 1
            before_imports = content[:end_pos]
            after_imports = content[end_pos:]
            
            traceback_import = '''
import traceback'''
            
            content = before_imports + traceback_import + after_imports
    
    # Buscar y mejorar los error handlers
    old_404_handler = '''@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Página no encontrada"}), 404'''
    
    new_404_handler = '''@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f"404: {request.url}")
    return jsonify({"error": "Página no encontrada"}), 404'''
    
    old_500_handler = '''@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500'''
    
    new_500_handler = '''@app.errorhandler(500)
def internal_error(error):
    logger.error("500: %s\n%s", error, traceback.format_exc())
    return jsonify({"error": "Error interno del servidor"}), 500'''
    
    # Reemplazar handlers
    if old_404_handler in content:
        content = content.replace(old_404_handler, new_404_handler)
    
    if old_500_handler in content:
        content = content.replace(old_500_handler, new_500_handler)
    
    # Escribir el archivo actualizado
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Manejo de errores mejorado")
    print("🔧 Logging detallado agregado para errores 500")
    print("🔧 Logging de URLs para errores 404")

if __name__ == "__main__":
    improve_error_handling() 