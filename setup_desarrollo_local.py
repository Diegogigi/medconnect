#!/usr/bin/env python3
"""
Script para configurar el entorno de desarrollo local de MedConnect
Este script permite trabajar localmente usando la base de datos de Railway
sin afectar la configuración de producción.
"""

import os
import sys
from dotenv import load_dotenv


def setup_local_development():
    """Configura el entorno para desarrollo local"""

    print("🚀 Configurando MedConnect para desarrollo local...")
    print("=" * 60)

    # 1. Cargar variables de entorno desde archivo si existe
    env_file = "env_local.txt"
    if os.path.exists(env_file):
        print(f"📁 Cargando variables de entorno desde {env_file}...")
        load_dotenv(env_file)
        print("✅ Variables de entorno cargadas")
    else:
        print(f"⚠️ Archivo {env_file} no encontrado, usando configuración por defecto")

    # 2. Configurar variables de entorno para desarrollo local
    local_env_vars = {
        "DATABASE_URL": "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway",
        "SECRET_KEY": "medconnect-secret-key-2025-railway-production",
        "FLASK_ENV": "development",
        "DEBUG": "True",
        "PORT": "8000",
        "OPENROUTER_API_KEY": "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",
        "CORS_ORIGINS": "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:3000",
        "SESSION_COOKIE_SECURE": "False",
        "SESSION_COOKIE_HTTPONLY": "True",
        "SESSION_COOKIE_SAMESITE": "Lax",
    }

    print("\n🔧 Configurando variables de entorno...")
    for key, value in local_env_vars.items():
        if not os.environ.get(key):
            os.environ[key] = value
            print(f"  ✅ {key} = {value[:50]}{'...' if len(value) > 50 else ''}")
        else:
            print(
                f"  🔄 {key} = {os.environ[key][:50]}{'...' if len(os.environ[key]) > 50 else ''} (ya configurada)"
            )

    # 3. Verificar configuración
    print("\n🔍 Verificando configuración...")

    database_url = os.environ.get("DATABASE_URL")
    secret_key = os.environ.get("SECRET_KEY")
    flask_env = os.environ.get("FLASK_ENV")
    port = os.environ.get("PORT")

    print(
        f"  📊 DATABASE_URL: {'✅ Configurada' if database_url else '❌ No configurada'}"
    )
    print(f"  🔑 SECRET_KEY: {'✅ Configurada' if secret_key else '❌ No configurada'}")
    print(f"  🌍 FLASK_ENV: {flask_env}")
    print(f"  🚪 PORT: {port}")

    # 4. Mostrar información de acceso
    print("\n🌐 Información de acceso:")
    print(f"  🏠 URL Local: http://localhost:{port}")
    print(f"  🏠 URL Alternativa: http://127.0.0.1:{port}")
    print(f"  🔐 Login: http://localhost:{port}/login")
    print(f"  ❤️ Health Check: http://localhost:{port}/health")

    # 5. Credenciales de prueba
    print("\n👤 Credenciales de prueba:")
    print("  📧 Email: diego.castro.lagos@gmail.com")
    print("  🔒 Password: password123")
    print("  📧 Email: rodrigoandressilvabreve@gmail.com")
    print("  🔒 Password: password123")

    # 6. Instrucciones
    print("\n📋 Instrucciones:")
    print("  1. Ejecuta: python app.py")
    print("  2. Abre tu navegador en http://localhost:8000")
    print("  3. Inicia sesión con las credenciales de prueba")
    print("  4. ¡Ya puedes desarrollar localmente!")

    print("\n" + "=" * 60)
    print("✅ Configuración de desarrollo local completada")
    print("🚀 ¡Listo para desarrollar!")

    return True


def main():
    """Función principal"""
    try:
        setup_local_development()
    except Exception as e:
        print(f"❌ Error durante la configuración: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
