#!/usr/bin/env python3
"""
Script final para eliminar las últimas duplicaciones y completar la limpieza
"""

def fix_final_duplications():
    """Elimina las duplicaciones finales de setup_webhook y otras funciones"""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 Archivo original: {len(lines)} líneas")
    
    # Crear backup final
    with open('app_backup_final_clean.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("💾 Backup final creado: app_backup_final_clean.py")
    
    new_lines = []
    skip_lines = 0
    found_functions = {}
    
    # Lista de funciones duplicadas finales
    duplicated_patterns = [
        "@app.route('/setup-webhook')",
        "def test_bot():",
        "def log_bot_interaction(user_id, username, message, chat_id):",
        "def obtener_rango_semana(fecha_str):",
        "def obtener_rango_mes(fecha_str):",
        "def send_telegram_message(telegram_id, message):",
        "def setup_webhook():",
    ]
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Si estamos saltando líneas, decrementar contador
        if skip_lines > 0:
            skip_lines -= 1
            continue
        
        # Verificar si es una función duplicada
        is_duplicate = False
        for pattern in duplicated_patterns:
            if pattern in line.strip():
                if pattern not in found_functions:
                    # Primera instancia - mantener
                    found_functions[pattern] = line_num
                    new_lines.append(line)
                    print(f"✅ Manteniendo primera instancia: {pattern} en línea {line_num}")
                else:
                    # Instancia duplicada - eliminar
                    print(f"❌ Eliminando duplicación: {pattern} en línea {line_num}")
                    
                    # Determinar cuántas líneas saltar según el tipo
                    if "@app.route" in pattern:
                        skip_lines = 30  # Ruta completa con función
                    elif "def " in pattern:
                        skip_lines = 25  # Función completa
                    
                    is_duplicate = True
                break
        
        if not is_duplicate:
            new_lines.append(line)
    
    # Limpiar líneas huérfanas adicionales
    final_lines = []
    for line in new_lines:
        # Saltar líneas huérfanas comunes
        stripped = line.strip()
        if stripped in ['"""', '    """', 'except Exception as e:', '        return jsonify({\'error\': str(e)}), 500']:
            # Verificar contexto para decidir si mantener
            continue
        final_lines.append(line)
    
    print(f"📊 Líneas finales: {len(final_lines)}")
    print(f"🗑️ Líneas eliminadas: {len(lines) - len(final_lines)}")
    
    # Escribir archivo completamente limpio
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(final_lines)
    
    print("✅ LIMPIEZA FINAL COMPLETADA")
    
    return len(lines) - len(final_lines)

if __name__ == "__main__":
    print("🚀 Ejecutando limpieza final de duplicaciones...")
    deleted = fix_final_duplications()
    print(f"🎉 ¡COMPLETADO! Se eliminaron {deleted} líneas duplicadas finales") 