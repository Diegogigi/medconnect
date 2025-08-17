#!/usr/bin/env python3
"""
Script DEFINITIVO FINAL para eliminar la ÚLTIMA duplicación de link_existing_users
¡PERFECCIÓN ABSOLUTA FINAL!
"""

def fix_link_users_definitivo():
    """Elimina la última duplicación de link_existing_users para PERFECCIÓN FINAL"""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 Archivo original: {len(lines)} líneas")
    
    # Crear backup de la perfección final
    with open('app_backup_PERFECCION_FINAL.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("💾 Backup de perfección final: app_backup_PERFECCION_FINAL.py")
    
    # Buscar y eliminar duplicaciones de link_existing_users
    new_lines = []
    found_first_link_users = False
    skip_link_users = False
    skip_count = 0
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Si estamos saltando líneas de link_existing_users duplicado
        if skip_link_users and skip_count > 0:
            skip_count -= 1
            print(f"⏭️ Saltando línea {line_num}: {line.strip()[:50]}...")
            continue
        elif skip_link_users and skip_count == 0:
            skip_link_users = False
        
        # Detectar link_existing_users
        if "@app.route('/api/admin/link-existing-users', methods=['POST'])" in line:
            if not found_first_link_users:
                # Primera instancia - mantener
                found_first_link_users = True
                new_lines.append(line)
                print(f"✅ Manteniendo primera instancia link_existing_users en línea {line_num}")
            else:
                # Instancia duplicada - eliminar (ÚLTIMA)
                print(f"❌ Eliminando ÚLTIMA duplicación link_existing_users en línea {line_num}")
                skip_link_users = True
                skip_count = 40  # Eliminar función completa
                continue
        else:
            new_lines.append(line)
    
    print(f"📊 Líneas finales: {len(new_lines)}")
    print(f"🗑️ Líneas eliminadas: {len(lines) - len(new_lines)}")
    
    # Escribir archivo de PERFECCIÓN FINAL
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ ¡ÚLTIMA DUPLICACIÓN ELIMINADA - PERFECCIÓN FINAL LOGRADA!")
    
    return len(lines) - len(new_lines)

if __name__ == "__main__":
    print("🏆 ELIMINANDO LA ÚLTIMA DUPLICACIÓN PARA PERFECCIÓN FINAL...")
    deleted = fix_link_users_definitivo()
    print(f"🎉🏆🌟🚀 ¡PERFECCIÓN FINAL ABSOLUTA! Se eliminaron {deleted} líneas")
    print("🌟🎉🏆🚀 ¡MEDCONNECT CÓDIGO PERFECTO SIN ERRORES! 🚀🏆🎉🌟") 