#!/usr/bin/env python3
"""
Script para eliminar líneas huérfanas específicas que causan IndentationError
"""

def remove_orphaned_final():
    """Elimina líneas huérfanas específicas por número de línea"""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 Archivo original: {len(lines)} líneas")
    
    # Crear backup final
    with open('app_backup_remove_orphaned_final.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("💾 Backup creado: app_backup_remove_orphaned_final.py")
    
    # Líneas huérfanas a eliminar (en orden inverso)
    orphaned_lines = [
        7152,  # Segunda instancia - })
        7151,  # Segunda instancia - 'is_dir': ...
        7150,  # Segunda instancia - 'exists': ...
        7149,  # Segunda instancia - 'path': ...
        7148,  # Segunda instancia - 'index': i,
        5230,  # Primera instancia - línea vacía
        5229,  # Primera instancia - })
        5228,  # Primera instancia - 'is_dir': ...
        5227,  # Primera instancia - 'exists': ...
        5226,  # Primera instancia - 'path': ...
        5225,  # Primera instancia - 'index': i,
    ]
    
    print(f"🎯 Eliminando {len(orphaned_lines)} líneas huérfanas específicas...")
    
    # Eliminar líneas en orden inverso
    for line_num in sorted(orphaned_lines, reverse=True):
        if line_num <= len(lines):
            removed_line = lines[line_num - 1].strip()
            del lines[line_num - 1]  # Convertir a índice 0-based
            print(f"❌ Eliminada línea {line_num}: {removed_line[:50]}...")
    
    print(f"📊 Líneas finales: {len(lines)}")
    print(f"🗑️ Líneas huérfanas eliminadas: {len(orphaned_lines)}")
    
    # Escribir archivo completamente limpio
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ TODAS LAS LÍNEAS HUÉRFANAS ELIMINADAS")
    
    return len(orphaned_lines)

if __name__ == "__main__":
    print("🚀 Eliminando líneas huérfanas finales...")
    deleted = remove_orphaned_final()
    print(f"🎉 ¡LÍNEAS HUÉRFANAS ELIMINADAS! Se limpiaron {deleted} líneas")
    print("🏆 ¡ARCHIVO COMPLETAMENTE LIMPIO!") 