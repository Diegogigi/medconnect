#!/usr/bin/env python3
"""
Script para cambiar temporalmente al bot de prueba
"""

import shutil
import os

def backup_original_files():
    """Hace backup de los archivos originales"""
    files_to_backup = ['start.sh', 'Procfile']
    
    for file in files_to_backup:
        if os.path.exists(file):
            backup_name = f"{file}.backup"
            shutil.copy2(file, backup_name)
            print(f"✅ Backup creado: {backup_name}")

def create_test_procfile():
    """Crea un Procfile para el bot de prueba"""
    content = "web: python bot_simple_test.py\n"
    
    with open('Procfile', 'w') as f:
        f.write(content)
    print("✅ Procfile actualizado para bot de prueba")

def create_test_start_script():
    """Crea un start.sh simplificado para prueba"""
    content = '''#!/bin/bash

echo "🧪 === INICIANDO BOT DE PRUEBA ==="
echo "📅 Fecha: $(date)"
echo ""

# Verificar variables de entorno críticas
echo "🔍 === VERIFICANDO VARIABLES DE ENTORNO ==="
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN no configurado"
    exit 1
else
    echo "✅ TELEGRAM_BOT_TOKEN configurado"
fi

echo ""
echo "🤖 === INICIANDO BOT DE PRUEBA SIMPLIFICADO ==="

# Ejecutar bot de prueba
python bot_simple_test.py
'''
    
    with open('start.sh', 'w') as f:
        f.write(content)
    print("✅ start.sh actualizado para bot de prueba")

def restore_original_files():
    """Restaura los archivos originales"""
    files_to_restore = ['start.sh', 'Procfile']
    
    for file in files_to_restore:
        backup_name = f"{file}.backup"
        if os.path.exists(backup_name):
            shutil.copy2(backup_name, file)
            os.remove(backup_name)
            print(f"✅ Restaurado: {file}")

def main():
    """Función principal"""
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python switch_to_test_bot.py [test|restore]")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    if action == 'test':
        print("🧪 Cambiando a bot de prueba...")
        backup_original_files()
        create_test_procfile()
        create_test_start_script()
        print("")
        print("✅ Bot de prueba configurado!")
        print("📝 Haz commit y push para desplegar:")
        print("   git add .")
        print("   git commit -m 'Test: Bot de prueba simplificado'")
        print("   git push origin main")
        
    elif action == 'restore':
        print("🔄 Restaurando bot original...")
        restore_original_files()
        print("")
        print("✅ Bot original restaurado!")
        print("📝 Haz commit y push para restaurar:")
        print("   git add .")
        print("   git commit -m 'Restore: Bot original restaurado'")
        print("   git push origin main")
        
    else:
        print("❌ Acción inválida. Usa 'test' o 'restore'")
        sys.exit(1)

if __name__ == "__main__":
    main() 