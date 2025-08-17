#!/usr/bin/env python3
"""
Script específico para eliminar SOLO las duplicaciones de health_check
"""

def fix_health_check_only():
    """Elimina solo las duplicaciones específicas de health_check que causan error"""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 Archivo original: {len(lines)} líneas")
    
    # Crear backup específico
    with open('app_backup_fix_health_check.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("💾 Backup creado: app_backup_fix_health_check.py")
    
    # Buscar y eliminar SOLO las duplicaciones de health_check
    new_lines = []
    found_first_health = False
    skip_health = False
    skip_count = 0
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Si estamos saltando líneas de health_check duplicado
        if skip_health and skip_count > 0:
            skip_count -= 1
            print(f"⏭️ Saltando línea {line_num}: {line.strip()[:50]}...")
            continue
        elif skip_health and skip_count == 0:
            skip_health = False
        
        # Detectar health_check
        if "@app.route('/health')" in line:
            if not found_first_health:
                # Primera instancia - mantener
                found_first_health = True
                new_lines.append(line)
                print(f"✅ Manteniendo primera instancia health_check en línea {line_num}")
            else:
                # Instancia duplicada - eliminar (esta causa el error)
                print(f"❌ Eliminando duplicación health_check en línea {line_num}")
                skip_health = True
                skip_count = 35  # Eliminar función completa de health_check
                continue
        else:
            new_lines.append(line)
    
    print(f"📊 Líneas finales: {len(new_lines)}")
    print(f"🗑️ Líneas eliminadas: {len(lines) - len(new_lines)}")
    
    # Escribir archivo corregido
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ Duplicaciones específicas de health_check eliminadas")
    
    return len(lines) - len(new_lines)

if __name__ == "__main__":
    print("🎯 Eliminando SOLO las duplicaciones de health_check...")
    deleted = fix_health_check_only()
    print(f"🎉 ¡Error específico solucionado! Se eliminaron {deleted} líneas") 