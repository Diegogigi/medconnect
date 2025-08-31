#!/usr/bin/env python3
"""
Crear una versión limpia de app.py para PostgreSQL
"""


def create_clean_app():
    """Crear app.py limpio para PostgreSQL"""

    clean_app_content = '''# MedConnect - Aplicación Principal Flask
# Backend para plataforma de gestión médica con PostgreSQL

import os
import sys
import logging
import time
import random
import threading

# Configurar logging temprano para debugging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

logger.info("🚀 Iniciando MedConnect con PostgreSQL...")

try:
    logger.info("[PAQUETE] Importando Flask...")
    from flask import (
        Flask,
        render_template,
        request,
        jsonify,
        session,
        redirect,
        url_for,
        flash,
        make_response,
        send_from_directory,
        send_file,
        abort,
        Response,
    )
    logger.info("[OK] Flask importado exitosamente")

    logger.info("[PAQUETE] Importando Flask-CORS...")
    from flask_cors import CORS
    logger.info("[OK] Flask-CORS importado exitosamente")

    logger.info("[PAQUETE] Importando bibliotecas estándar...")
    import requests
    import json
    import tempfile
    from io import BytesIO
    from datetime import datetime, timedelta
    logger.info("[OK] Bibliotecas estándar importadas")

    logger.info("[PAQUETE] Importando PostgreSQL...")
    import psycopg2
    from psycopg2.extras import RealDictCursor
    logger.info("[OK] PostgreSQL importado exitosamente")

    logger.info("[PAQUETE] Importando módulos locales...")
    from auth_manager import AuthManager
    from postgresql_db_manager import PostgreSQLDBManager
    logger.info("[OK] Módulos locales importados")

    logger.info("[PAQUETE] Importando otras dependencias...")
    from werkzeug.utils import secure_filename
    import uuid
    from werkzeug.security import generate_password_hash, check_password_hash
    import secrets
    logger.info("[OK] Todas las importaciones completadas exitosamente")

    # Configurar PostgreSQL
    logger.info("[CONFIG] Configurando PostgreSQL...")
    try:
        postgres_db = PostgreSQLDBManager()
        if postgres_db.is_connected():
            logger.info("[OK] PostgreSQL configurado exitosamente")
        else:
            logger.error("[ERROR] No se pudo conectar a PostgreSQL")
            postgres_db = None
    except Exception as e:
        logger.error(f"[ERROR] Error configurando PostgreSQL: {e}")
        postgres_db = None

    # Importar módulo Copilot Health
    logger.info("[PAQUETE] Importando Copilot Health...")
    try:
        from copilot_health import copilot_health
        COPILOT_HEALTH_AVAILABLE = True
        logger.info("[OK] Módulo Copilot Health cargado exitosamente")
    except ImportError as e:
        COPILOT_HEALTH_AVAILABLE = False
        logger.warning(f"[ADVERTENCIA] Módulo Copilot Health no disponible: {e}")
    except Exception as e:
        COPILOT_HEALTH_AVAILABLE = False
        logger.error(f"[ERROR] Error cargando Copilot Health: {e}")

except Exception as e:
    logger.error(f"[ERROR] Error durante las importaciones: {e}")
    logger.error(f"[ERROR] Tipo de error: {type(e).__name__}")
    import traceback
    logger.error(f"[ERROR] Traceback completo: {traceback.format_exc()}")
    raise

# Inicializar Flask
app = Flask(__name__)

# Configuración básica
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['FLASK_ENV'] = os.environ.get('FLASK_ENV', 'development')

# Variables globales
start_time = time.time()
auth_manager = AuthManager()

# Configurar CORS
CORS(app)

# Configurar archivos estáticos para producción
try:
    from whitenoise import WhiteNoise
    app.wsgi_app = WhiteNoise(
        app.wsgi_app,
        root=os.path.join(app.root_path, "static"),
        prefix="static/"
    )
    logger.info("[OK] WhiteNoise configurado para archivos estáticos")
except ImportError:
    logger.warning("[ADVERTENCIA] WhiteNoise no disponible, usando configuración estándar")

# Rutas básicas
@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/login')
def login():
    """Página de login"""
    return render_template('login.html')

@app.route('/professional')
def professional():
    """Dashboard profesional"""
    return render_template('professional.html')

@app.route('/health')
def health_check():
    """Health check para Railway"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': time.time() - start_time,
        'database': 'connected' if postgres_db and postgres_db.is_connected() else 'disconnected'
    })

@app.route('/favicon.ico')
def favicon():
    """Favicon"""
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Iniciando servidor en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
'''

    with open("app_clean.py", "w", encoding="utf-8") as f:
        f.write(clean_app_content)

    print("✅ app_clean.py creado")


if __name__ == "__main__":
    create_clean_app()
    print("🎉 Versión limpia de app.py creada")
    print("💡 Reemplaza app.py con app_clean.py para solucionar el problema")
