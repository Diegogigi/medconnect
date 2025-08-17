#!/usr/bin/env python3
"""
Script para limpiar las SEGUNDAS líneas huérfanas de test_complete
"""

def clean_second_orphans():
    """Limpia las segundas líneas huérfanas de test_complete"""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 Archivo original: {len(lines)} líneas")
    
    # Crear backup
    with open('app_backup_clean_second_orphans.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("💾 Backup creado: app_backup_clean_second_orphans.py")
    
    # Las segundas líneas huérfanas están alrededor de la línea 7055
    new_lines = []
    skip_orphans = False
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Detectar inicio de las segundas líneas huérfanas
        if line_num == 7055 and "'GOOGLE_SERVICE_ACCOUNT_JSON'" in line:
            skip_orphans = True
            print(f"🎯 Detectando inicio de segundas líneas huérfanas en línea {line_num}")
            continue
        
        # Detectar final de líneas huérfanas
        if skip_orphans and (line.strip().startswith('@app.route') or line.strip().startswith('def ') or 
                            (line.strip().startswith('#') and 'Ruta' in line) or
                            line.strip().startswith('if __name__')):
            skip_orphans = False
            print(f"✅ Fin de segundas líneas huérfanas en línea {line_num}")
            new_lines.append(line)
            continue
        
        if skip_orphans:
            print(f"⏭️ Saltando segunda línea huérfana {line_num}: {line.strip()[:50]}...")
            continue
        
        new_lines.append(line)
    
    print(f"📊 Líneas finales: {len(new_lines)}")
    print(f"🗑️ Segundas líneas huérfanas eliminadas: {len(lines) - len(new_lines)}")
    
    # Escribir archivo FINALMENTE LIMPIO
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ ¡SEGUNDAS LÍNEAS HUÉRFANAS ELIMINADAS - ARCHIVO FINALMENTE LIMPIO!")
    
    return len(lines) - len(new_lines)

if __name__ == "__main__":
    print("🧹 LIMPIANDO SEGUNDAS LÍNEAS HUÉRFANAS...")
    deleted = clean_second_orphans()
    print(f"🎉🏆 ¡SEGUNDAS LÍNEAS HUÉRFANAS ELIMINADAS! Se eliminaron {deleted} líneas")
    print("🚀🌟 ¡ARCHIVO APP.PY FINALMENTE PERFECTO! 🌟🚀") 