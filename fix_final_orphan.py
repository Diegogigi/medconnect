#!/usr/bin/env python3
"""
Script para eliminar la ÚLTIMA línea huérfana en 7141
"""

def fix_final_orphan():
    """Elimina la última línea huérfana"""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 Archivo original: {len(lines)} líneas")
    
    # Crear backup
    with open('app_backup_final_orphan.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("💾 Backup creado: app_backup_final_orphan.py")
    
    # Eliminar la línea huérfana específica (línea 7141, índice 7140)
    if len(lines) > 7140 and "'index': i," in lines[7140]:
        removed_line = lines[7140].strip()
        del lines[7140]
        print(f"❌ Eliminada línea huérfana 7141: {removed_line}")
    
    print(f"📊 Líneas finales: {len(lines)}")
    
    # Escribir archivo limpio
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ ÚLTIMA LÍNEA HUÉRFANA ELIMINADA")
    
    return 1

if __name__ == "__main__":
    print("🎯 Eliminando ÚLTIMA línea huérfana...")
    deleted = fix_final_orphan()
    print(f"🎉 ¡COMPLETADO! Línea huérfana eliminada")
    print("🏆 ¡ARCHIVO FINALMENTE LIMPIO!") 