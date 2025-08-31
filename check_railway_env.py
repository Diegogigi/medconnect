#!/usr/bin/env python3
"""
Script para verificar variables de entorno en Railway
"""

import os


def check_railway_environment():
    """Verifica las variables de entorno necesarias para Railway"""

    print("🔍 Verificando variables de entorno para Railway...")
    print("=" * 50)

    # Variables críticas
    critical_vars = {
        "DATABASE_URL": "Conexión a PostgreSQL",
        "SECRET_KEY": "Seguridad de sesiones",
        "FLASK_ENV": "Entorno de Flask",
        "OPENROUTER_API_KEY": "API de IA",
        "PORT": "Puerto de la aplicación",
    }

    # Variables opcionales
    optional_vars = {
        "TELEGRAM_BOT_TOKEN": "Bot de Telegram",
        "CORS_ORIGINS": "Configuración CORS",
    }

    print("📋 Variables Críticas:")
    all_critical_ok = True
    for var, description in critical_vars.items():
        value = os.environ.get(var)
        if value:
            # Ocultar valores sensibles
            if "KEY" in var or "SECRET" in var or "PASSWORD" in var:
                display_value = f"{value[:10]}..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: NO CONFIGURADA")
            all_critical_ok = False

    print("\n📋 Variables Opcionales:")
    for var, description in optional_vars.items():
        value = os.environ.get(var)
        if value:
            print(f"  ✅ {var}: Configurada")
        else:
            print(f"  ⚠️ {var}: No configurada (opcional)")

    print("\n" + "=" * 50)

    if all_critical_ok:
        print("🎉 Todas las variables críticas están configuradas")
        print("✅ La aplicación debería funcionar correctamente en Railway")
    else:
        print("⚠️ Faltan variables críticas")
        print("🔧 Configura las variables faltantes en Railway Dashboard")

    # Verificar específicamente DATABASE_URL
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        print(f"\n🗄️ DATABASE_URL encontrada:")
        if "railway" in database_url:
            print("  ✅ URL de Railway detectada")
        else:
            print("  ⚠️ URL no parece ser de Railway")
    else:
        print("\n❌ DATABASE_URL NO CONFIGURADA")
        print("   Esto causará errores 502 en Railway")

    return all_critical_ok


if __name__ == "__main__":
    check_railway_environment()
