#!/usr/bin/env python3
"""
Script simple para verificar variables de entorno en Railway
"""

import os
import json

def main():
    print("🔍 === VERIFICACIÓN DE VARIABLES DE ENTORNO EN RAILWAY ===")
    print("")
    
    # Variables críticas
    vars_to_check = [
        'TELEGRAM_BOT_TOKEN',
        'GOOGLE_SHEETS_ID', 
        'GOOGLE_SERVICE_ACCOUNT_JSON'
    ]
    
    all_ok = True
    
    for var in vars_to_check:
        value = os.environ.get(var)
        if value:
            if var == 'GOOGLE_SERVICE_ACCOUNT_JSON':
                print(f"✅ {var}: Configurado ({len(value)} caracteres)")
                try:
                    json_data = json.loads(value)
                    print(f"   📝 Proyecto: {json_data.get('project_id', 'N/A')}")
                except:
                    print(f"   ❌ JSON inválido")
                    all_ok = False
            else:
                # Mostrar solo los primeros y últimos caracteres por seguridad
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {var}: {masked}")
        else:
            print(f"❌ {var}: NO CONFIGURADO")
            all_ok = False
    
    print("")
    if all_ok:
        print("🎉 ¡Todas las variables están configuradas!")
    else:
        print("⚠️ Faltan variables críticas. Configúralas en Railway.")
    
    print("")
    print("📋 Para configurar variables en Railway:")
    print("1. Ve a tu proyecto en railway.app")
    print("2. Click en Variables")
    print("3. Agrega las variables faltantes")
    print("4. Redeploy el proyecto")

if __name__ == "__main__":
    main() 