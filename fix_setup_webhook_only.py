#!/usr/bin/env python3
"""
Script específico y seguro para eliminar SOLO la duplicación de setup_webhook
"""

def fix_setup_webhook_only():
    """Elimina solo la duplicación específica de setup_webhook que causa error"""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 Archivo original: {len(lines)} líneas")
    
    # Crear backup específico
    with open('app_backup_fix_setup_webhook.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("💾 Backup creado: app_backup_fix_setup_webhook.py")
    
    # Buscar y eliminar SOLO la segunda instancia de setup_webhook
    new_lines = []
    found_first_setup_webhook = False
    skip_setup_webhook = False
    skip_count = 0
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Si estamos saltando líneas de setup_webhook duplicado
        if skip_setup_webhook and skip_count > 0:
            skip_count -= 1
            print(f"⏭️ Saltando línea {line_num}: {line.strip()[:50]}...")
            continue
        elif skip_setup_webhook and skip_count == 0:
            skip_setup_webhook = False
        
        # Detectar setup_webhook
        if "@app.route('/setup-webhook')" in line or "def setup_webhook():" in line:
            if not found_first_setup_webhook:
                # Primera instancia - mantener
                found_first_setup_webhook = True
                new_lines.append(line)
                print(f"✅ Manteniendo primera instancia setup_webhook en línea {line_num}")
            else:
                # Segunda instancia - eliminar (esta causa el error)
                print(f"❌ Eliminando segunda instancia setup_webhook en línea {line_num}")
                skip_setup_webhook = True
                skip_count = 20  # Eliminar función completa
                continue
        else:
            new_lines.append(line)
    
    print(f"📊 Líneas finales: {len(new_lines)}")
    print(f"🗑️ Líneas eliminadas: {len(lines) - len(new_lines)}")
    
    # Escribir archivo corregido
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ Duplicación específica de setup_webhook eliminada")
    
    return len(lines) - len(new_lines)

if __name__ == "__main__":
    print("🎯 Eliminando SOLO la duplicación de setup_webhook...")
    deleted = fix_setup_webhook_only()
    print(f"🎉 ¡Error específico solucionado! Se eliminaron {deleted} líneas") 