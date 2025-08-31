#!/usr/bin/env python3
"""
Script para eliminar secrets hard-coded
"""


def fix_hardcoded_secrets():
    """Elimina secrets hard-coded del código"""

    print("🔧 Eliminando secrets hard-coded...")

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar la clase Config
    old_config = """class Config:
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
    PORT = int(os.environ.get("PORT", "8000"))  # Default coherente con PaaS"""

    new_config = """class Config:
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

    # Reemplazar en el contenido
    if old_config in content:
        content = content.replace(old_config, new_config)

        # Escribir el archivo actualizado
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Secrets hard-coded eliminados")
        print("🔧 Ahora las variables críticas son requeridas")
        print(
            "⚠️ IMPORTANTE: Asegúrate de que SECRET_KEY y DATABASE_URL estén configuradas en Railway"
        )
    else:
        print("❌ No se encontró la clase Config original")


if __name__ == "__main__":
    fix_hardcoded_secrets()
