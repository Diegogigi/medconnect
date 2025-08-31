#!/usr/bin/env python3
"""
Script para configurar variables de entorno directamente en el código para Railway
"""


def fix_railway_env_variables():
    """Configura variables de entorno directamente en el código para Railway"""

    print("🔧 Configurando variables de entorno para Railway...")

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar la sección de configuración
    config_start = "# --- Config"

    if config_start in content:
        # Encontrar el inicio de la clase Config
        start_pos = content.find(config_start)

        # Buscar el final de la clase Config
        end_marker = "app = Flask(__name__)"
        end_pos = content.find(end_marker, start_pos)

        if end_pos != -1:
            # Extraer la clase Config actual
            config_section = content[start_pos:end_pos]

            # Nueva configuración con valores por defecto para Railway
            new_config = """# --- Config
class Config:
    # Variables de entorno con valores por defecto para Railway
    SECRET_KEY = os.environ.get("SECRET_KEY", "medconnect-secret-key-2025-railway-production")
    FLASK_ENV = os.environ.get("FLASK_ENV", "production")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")  # opcional
    TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    PREFERRED_URL_SCHEME = "https" if "medconnect.cl" in os.environ.get("CUSTOM_DOMAIN","") else "http"
    
    # Configuración específica para Railway PostgreSQL
    DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@postgres.railway.internal:5432/railway")
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")
    PORT = int(os.environ.get("PORT", "5000"))"""

            # Reemplazar la sección de configuración
            content = content.replace(config_section, new_config)

            # Escribir el archivo actualizado
            with open("app.py", "w", encoding="utf-8") as f:
                f.write(content)

            print("✅ Variables de entorno configuradas para Railway")
            print("🔧 Ahora el código tiene valores por defecto para Railway")
        else:
            print("❌ No se encontró el final de la clase Config")
    else:
        print("❌ No se encontró la sección de configuración")


if __name__ == "__main__":
    fix_railway_env_variables()
