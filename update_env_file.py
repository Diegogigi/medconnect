#!/usr/bin/env python3
"""
Script para actualizar el archivo .env con la nueva API key
"""

from datetime import datetime


def update_env_file():
    """Actualizar archivo .env con la nueva API key"""
    env_content = f"""# MedConnect - Variables de Entorno Local
# Configuración actualizada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Configuración de Flask
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=clave-secreta-local-desarrollo

# Configuración del dominio
DOMAIN=localhost:5000
BASE_URL=http://localhost:5000

# Configuración de OpenRouter (API key actualizada)
OPENROUTER_API_KEY=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

# Configuración de logging
LOG_LEVEL=INFO

# Configuración de Railway (para producción)
PORT=5000
RAILWAY_ENVIRONMENT=development
"""

    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✅ Archivo .env actualizado exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error actualizando .env: {e}")
        return False


if __name__ == "__main__":
    print("📝 Actualizando archivo .env con nueva API key...")
    update_env_file()
