#!/usr/bin/env python3
"""
Configuración para desarrollo local OFFLINE
Esta configuración permite desarrollar sin conexión a la base de datos de Railway
"""

import os
import sys


def configurar_desarrollo_offline():
    """Configura el entorno para desarrollo local sin base de datos externa"""

    print("🔧 Configurando MedConnect para desarrollo OFFLINE...")
    print("=" * 60)

    # Variables de entorno para desarrollo offline
    offline_config = {
        # No usar base de datos externa
        "DATABASE_URL": "",
        "PGHOST": "",
        "PGDATABASE": "",
        "PGUSER": "",
        "PGPASSWORD": "",
        "PGPORT": "",
        # Configuración de Flask
        "SECRET_KEY": "dev-secret-key-local-offline-12345",
        "FLASK_ENV": "development",
        "DEBUG": "True",
        "PORT": "8000",
        # Configuración de cookies para desarrollo local
        "SESSION_COOKIE_SECURE": "False",
        "SESSION_COOKIE_HTTPONLY": "True",
        "SESSION_COOKIE_SAMESITE": "Lax",
        # CORS para desarrollo local
        "CORS_ORIGINS": "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:3000",
        # APIs opcionales (vacías para desarrollo offline)
        "OPENROUTER_API_KEY": "",
        "TELEGRAM_BOT_TOKEN": "",
    }

    print("🔧 Configurando variables de entorno offline...")
    for key, value in offline_config.items():
        os.environ[key] = value
        if key in ["SECRET_KEY", "OPENROUTER_API_KEY", "TELEGRAM_BOT_TOKEN"]:
            print(f"  ✅ {key} = {'[CONFIGURADA]' if value else '[VACÍA]'}")
        else:
            print(f"  ✅ {key} = {value}")

    print("\n🌐 Información de acceso:")
    print("  🏠 URL Local: http://localhost:8000")
    print("  🏠 URL Alternativa: http://127.0.0.1:8000")
    print("  🔐 Login: http://localhost:8000/login")
    print("  ❤️ Health Check: http://localhost:8000/health")

    print("\n👤 Credenciales de prueba (datos simulados):")
    print("  📧 Email: diego.castro.lagos@gmail.com")
    print("  🔒 Password: password123")
    print("  📧 Email: rodrigoandressilvabreve@gmail.com")
    print("  🔒 Password: password123")

    print("\n📋 Características del modo offline:")
    print("  ✅ Funciona sin conexión a internet")
    print("  ✅ Usa datos simulados para desarrollo")
    print("  ✅ Todas las funcionalidades disponibles")
    print("  ✅ No afecta la base de datos de Railway")
    print("  ✅ Ideal para desarrollo y pruebas")

    print("\n" + "=" * 60)
    print("✅ Configuración offline completada")
    print("🚀 ¡Listo para desarrollar sin conexión!")

    return True


def main():
    """Función principal"""
    try:
        configurar_desarrollo_offline()
    except Exception as e:
        print(f"❌ Error durante la configuración: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
