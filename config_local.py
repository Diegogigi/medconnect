#!/usr/bin/env python3
"""
Configuración para desarrollo local
"""

import os

# Configuración para desarrollo local
LOCAL_CONFIG = {
    "FLASK_ENV": "development",
    "SECRET_KEY": "dev-secret-key-local-12345",
    "PORT": 5000,
    "DEBUG": True,
    "TESTING": True,
    "DATABASE_URL": None,  # No usar PostgreSQL local por defecto
    "TELEGRAM_BOT_TOKEN": "",
    "OPENROUTER_API_KEY": "",
}


def setup_local_environment():
    """Configura el entorno para desarrollo local"""
    print("🔧 Configurando entorno de desarrollo local...")

    # Establecer variables de entorno para desarrollo
    for key, value in LOCAL_CONFIG.items():
        if not os.environ.get(key):
            os.environ[key] = str(value)
            print(f"  ✅ {key} = {value}")

    print("✅ Entorno de desarrollo configurado")


if __name__ == "__main__":
    setup_local_environment()
