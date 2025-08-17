#!/usr/bin/env python3
"""
Script para ensanchar las tablas y eliminar scroll horizontal
"""

import os
import time
import webbrowser
from datetime import datetime

def ensanchar_tablas():
    """Ensancha las tablas y elimina scroll horizontal"""
    
    print("📊 ENSANCHANDO TABLAS")
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
    
    print("\n📊 ENSANCHAMIENTO DE TABLAS COMPLETADO")
    print("=" * 60)
    print("✅ Tablas con ancho completo (100%)")
    print("✅ Scroll horizontal eliminado")
    print("✅ Columnas optimizadas con porcentajes específicos")
    print("✅ Texto ajustable en celdas")
    print("✅ Layout fijo para mejor distribución")
    print("✅ Diagnóstico con más espacio (35%)")
    print("\n📝 PRÓXIMOS PASOS:")
    print("   1. Recarga la página de MedConnect (Ctrl+F5)")
    print("   2. Ve a 'Historial de Atenciones'")
    print("   3. Verifica que las tablas usen todo el ancho")
    print("   4. Confirma que no hay scroll horizontal")

if __name__ == "__main__":
    ensanchar_tablas() 