#!/usr/bin/env python3
"""
Script para hacer las variables de entorno flexibles
"""


def fix_env_variables_flexible():
    """Hace las variables de entorno flexibles para desarrollo y producción"""

    print("🔧 Haciendo variables de entorno flexibles...")

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar la clase Config
    old_config = """class Config:
    # Variables de entorno críticas (sin defaults para seguridad)
    SECRET_KEY = os.environ["SECRET_KEY"]  # Requerida
    DATABASE_URL = os.environ["DATABASE_URL"]  # Requerida
    
    # Variables de entorno opcionales
    FLASK_ENV = os.environ.get("FLASK_ENV", "production")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")  # opcional
    TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    PREFERRED_URL_SCHEME = "https" if "medconnect.cl" in os.environ.get("CUSTOM_DOMAIN","") else "http"
    
    # Configuración específica para Railway
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")  # opcional
    PORT = int(os.environ.get("PORT", "8000"))  # Default coherente con PaaS"""

    new_config = """class Config:
    # Variables de entorno críticas (con fallbacks para desarrollo)
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-local-12345")
    DATABASE_URL = os.environ.get("DATABASE_URL", "")  # Vacía para desarrollo
    
    # Variables de entorno opcionales
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")  # opcional
    TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    PREFERRED_URL_SCHEME = "https" if "medconnect.cl" in os.environ.get("CUSTOM_DOMAIN","") else "http"
    
    # Configuración específica para Railway
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")  # opcional
    PORT = int(os.environ.get("PORT", "8000"))  # Default coherente con PaaS"""

    # Reemplazar en el contenido
    if old_config in content:
        content = content.replace(old_config, new_config)

        # Escribir el archivo actualizado
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Variables de entorno hechas flexibles")
        print("🔧 Ahora funcionará tanto en desarrollo local como en Railway")
        print("🔧 Desarrollo local: Usa valores por defecto")
        print("🔧 Railway: Usa variables de entorno configuradas")
    else:
        print("❌ No se encontró la clase Config original")


if __name__ == "__main__":
    fix_env_variables_flexible()
