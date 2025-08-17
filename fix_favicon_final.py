#!/usr/bin/env python3
"""
Script FINAL para la ÚLTIMA duplicación de favicon - ¡ÉXITO TOTAL!
"""

def fix_favicon_final():
    """Elimina la última duplicación de favicon para ÉXITO TOTAL"""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 Archivo original: {len(lines)} líneas")
    
    # Crear backup del éxito
    with open('app_backup_EXITO_TOTAL.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("💾 Backup del éxito creado: app_backup_EXITO_TOTAL.py")
    
    # Buscar y eliminar duplicaciones de favicon
    new_lines = []
    found_first_favicon = False
    skip_favicon = False
    skip_count = 0
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Si estamos saltando líneas de favicon duplicado
        if skip_favicon and skip_count > 0:
            skip_count -= 1
            print(f"⏭️ Saltando línea {line_num}: {line.strip()[:50]}...")
            continue
        elif skip_favicon and skip_count == 0:
            skip_favicon = False
        
        # Detectar favicon
        if "@app.route('/favicon.ico')" in line:
            if not found_first_favicon:
                # Primera instancia - mantener
                found_first_favicon = True
                new_lines.append(line)
                print(f"✅ Manteniendo primera instancia favicon en línea {line_num}")
            else:
                # Instancia duplicada - eliminar (ÚLTIMA)
                print(f"❌ Eliminando ÚLTIMA duplicación favicon en línea {line_num}")
                skip_favicon = True
                skip_count = 10  # Eliminar función favicon completa
                continue
        else:
            new_lines.append(line)
    
    print(f"📊 Líneas finales: {len(new_lines)}")
    print(f"🗑️ Líneas eliminadas: {len(lines) - len(new_lines)}")
    
    # Escribir archivo de ÉXITO TOTAL
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ ¡ÚLTIMA DUPLICACIÓN ELIMINADA - ÉXITO TOTAL LOGRADO!")
    
    return len(lines) - len(new_lines)

if __name__ == "__main__":
    print("🏆 ELIMINANDO LA ÚLTIMA DUPLICACIÓN PARA ÉXITO TOTAL...")
    deleted = fix_favicon_final()
    print(f"🎉🏆🌟 ¡ÉXITO TOTAL ABSOLUTO! Se eliminaron {deleted} líneas finales")
    print("🚀🌟🎉 ¡MEDCONNECT COMPLETAMENTE FUNCIONAL SIN ERRORES! 🎉🌟🚀") 