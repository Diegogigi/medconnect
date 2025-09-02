#!/usr/bin/env python3
"""
Script para cambiar el fondo principal a blanco puro
"""

def fix_background_white():
    """Cambia el fondo principal a blanco puro"""
    
    print("⚪ Cambiando fondo principal a blanco puro...")
    
    # Leer el archivo actual
    with open('templates/login.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Cambiar el fondo principal a blanco puro
    content = content.replace(
        'background: #f8fafc;',
        'background: white;'
    )
    
    # Escribir el archivo actualizado
    with open('templates/login.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fondo actualizado:")
    print("   - Fondo principal: blanco puro")
    print("   - Panel izquierdo: gradiente #6366f1 a #8b5cf6 (sin cambios)")
    print("   - Panel derecho: blanco (sin cambios)")

if __name__ == "__main__":
    fix_background_white() 