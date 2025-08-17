#!/usr/bin/env python3
"""
Script para limpiar líneas huérfanas que causan errores de indentación
"""

def clean_orphaned_indent():
    """Limpia líneas huérfanas específicas que causan errores de indentación"""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 Archivo original: {len(lines)} líneas")
    
    # Crear backup
    with open('app_backup_clean_indent.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("💾 Backup creado: app_backup_clean_indent.py")
    
    # Encontrar y eliminar líneas huérfanas específicas
    new_lines = []
    skip_orphans = False
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Detectar el inicio de líneas huérfanas (después de la línea 5455)
        if line_num == 5456 and line.strip() == '':
            skip_orphans = True
            print(f"🎯 Detectando inicio de líneas huérfanas en línea {line_num}")
            continue
        
        # Detectar el final de líneas huérfanas (cuando encontremos if __name__)
        if skip_orphans and line.strip().startswith('if __name__'):
            skip_orphans = False
            print(f"✅ Fin de líneas huérfanas en línea {line_num}")
            new_lines.append(line)
            continue
        
        if skip_orphans:
            print(f"⏭️ Saltando línea huérfana {line_num}: {line.strip()[:50]}...")
            continue
        
        new_lines.append(line)
    
    print(f"📊 Líneas finales: {len(new_lines)}")
    print(f"🗑️ Líneas huérfanas eliminadas: {len(lines) - len(new_lines)}")
    
    # Escribir archivo completamente limpio
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ ¡LÍNEAS HUÉRFANAS DE INDENTACIÓN ELIMINADAS!")
    
    return len(lines) - len(new_lines)

if __name__ == "__main__":
    print("🧹 Limpiando líneas huérfanas de indentación...")
    deleted = clean_orphaned_indent()
    print(f"🎉 ¡Líneas huérfanas eliminadas! Se limpiaron {deleted} líneas")
    print("🏆 ¡ARCHIVO COMPLETAMENTE LIMPIO!") 